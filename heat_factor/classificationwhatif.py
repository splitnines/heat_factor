import requests
from bs4 import BeautifulSoup
import numpy as np


classification_dict = {
    'GM': 95, 'M': 85, 'A': 75, 'B': 60, 'C': 40, 'D': 2, 'U': 0,
}

next_class_up = {
    'M': 'GM', 'A': 'M', 'B': 'A', 'C': 'B', 'D': 'C',
}

reverse_classification_dict = {
    95: 'GM', 85: 'M', 75: 'A', 60: 'B', 40: 'C', 2: 'D', 0: 'U',
}


class ClassificationWhatIf:
    """Provides an interface to uspsa.org used to calculate the percent score
       a shooter needs in thier next classifier to move up in classification.
    """

    def __init__(self, mem_num, division):
        """
        Arguments:
            mem_num {str} -- USPSA membership number to query
            division {str} -- USPSA division to check
        """
        self.mem_num = mem_num
        self.division = division

        self.bs = http_get(self.mem_num, self.division)
        self.current_pct = get_classification_pct(self.bs, self.division)
        self.shooter_class = get_classification_letter(self.bs, self.division)

    def get_upped(self):
        """
        Returns:
            [float] -- the percent needed for a shooter to move up a
                       classification level.
        """
        scores = get_scores(self.bs, self.division)

        return (
            round(
                (classification_dict[next_class_up[self.shooter_class]]
                 * (scores['count'] + 1)) - scores['sum'], 4
            )
        )

    def get_initial(self):
        """Used to get the initial classification of an
           unclassified shooter.

        Raises:
            ValueError: if the member number does not have enough scores on
                         record raise ValueError, needs at least 3 scores.

        Returns:
            [dict] -- keys are the classification letter, values are the
                      percent score needed to achieve that class.
        """
        scores = get_scores(self.bs, self.division)

        if self.shooter_class == 'U':

            if scores['count'] > 2:

                return calc_initial(scores['sum'], scores['count'])

            raise Exception('Not enough scores on record.')

    def get_shooter_class(self):
        """
        Returns:
            [str] -- the shooters current classification
        """
        return self.shooter_class

    def get_next_class(self):
        """
        Raises:
            AttributeError: if shooters current class is 'U'

        Returns:
            [str] -- contains the letter for the next classification up from
                     current class.
        """
        if self.shooter_class == 'U':

            raise Exception(
                'Unclassified shooter.  Use method get_initial().'
            )

        return next_class_up[self.shooter_class]


def http_get(mem_num, division):
    """Scrapes the uspsa.org classification lookup page.

    Arguments:
        mem_num {str} -- the uspsa membership number to query
        division {str} -- uspsa division

    Raises:
        AttributeError: if no data if found on uspsa.org for mem_num/division
                        combo.

    Returns:
        [object] -- the BeautifulSoup object with the data from uspsa.org
    """
    if division != 'PCC':
        division_search = division.title().replace(' ', '_')

    else:
        division_search = division.upper().replace(' ', '_')

    http_resp = requests.get(f'https://uspsa.org/classification/{mem_num}')

    bs = BeautifulSoup(http_resp.text, 'lxml')

    if bs.find('tbody', {'id': f'{division_search}-dropDown'}) is None:

        raise AttributeError

    return bs


def get_classifier_scores(bs, division):
    """Retreives the valid classifier scores that make up the shooters
       current classification.

    Arguments:
        bs {object} -- BeautifulSoup object from the uspsa.org scrape.
        division {str} -- uspsa division

    Yields:
        [tuple] -- str containing the classifier code, must be 'Y' and a
                   float containing the percent for that code.
    """
    if division != 'PCC':
        division_search = division.title().replace(' ', '_')

    else:
        division_search = division.upper().replace(' ', '_')

    table_body = bs.find('tbody', {'id': f'{division_search}-dropDown'})
    table_rows = table_body.find_all('tr')

    for row in table_rows[1:]:
        if str(row.find_all('td')[3].text.strip()) == 'Y':

            yield (
                str(row.find_all('td')[3].text.strip()),
                float(str(row.find_all('td')[4].text.strip()))
            )


def get_classification_pct(bs, division):
    """Retrieves shooters current classification percent.

    Arguments:
        bs {object} -- BeautifulSoup object from the uspsa.org scrape.
        division {str} -- uspsa division

    Raises:
        AttributeError: if member number is no longer active the class on
                        uspsa.org is set to 'X'.

    Returns:
        [float] -- current classification percent for member/division combo.
    """
    table_body = bs.find_all('tbody')[2]
    rows = table_body.find_all('tr')

    for row in rows:
        header = row.find_all('th')
        data = row.find_all('td')

        if [i.text.strip() for i in header][0] == division:

            classification_pct = (
                [i.text.strip() for i in data][1].split(': ')[1]
            )

            if classification_pct == 'X':

                raise AttributeError

            return float(classification_pct)

    return None


def get_classification_letter(bs, division):
    """Retrieves shooters current classification percent.

    Arguments:
        bs {object} -- BeautifulSoup object from the uspsa.org scrape.
        division {str} -- uspsa division

    Raises:
        AttributeError: if member number is no longer active the class on
                        uspsa.org is set to 'X'.

    Returns:
        [str] -- the shooters current classification letter.
    """
    table_body = bs.find_all('tbody')[2]
    rows = table_body.find_all('tr')

    for row in rows:
        header = row.find_all('th')
        data = row.find_all('td')

        if [i.text.strip() for i in header][0] == division:

            classification_letter = (
                [i.text.strip() for i in data][0].split(': ')[1]
            )

            if classification_letter == 'X':

                raise AttributeError

            return classification_letter

    return None


def get_scores(bs, division):
    """Calculate the sum of the shooters most recent valid classifier scores.

    Arguments:
        bs {object} -- BeautifulSoup object from the uspsa.org scrape.
        division {str} -- uspsa division

    Returns:
        [dict] -- with 2 keys, a float representing the sum of valid scores
                  on record and an int containing the count of valid scores
                  on record.
    """
    scores = {
        'sum': 0,
        'count': 0,
    }

    for score in get_classifier_scores(bs, division):

        if scores['count'] < 5:

            scores['sum'] += score[1]
            scores['count'] += 1

    return scores


def calc_initial(score_sum, score_count):
    """Performs a "reverse" calculation to determine what percent an
       unclassified shooter needs on thier next classifier to receive an
       initial classification.

    Arguments:
        score_sum {float} -- some of valid scores on record.
        score_count {int} -- count of valid scores on record.

    Returns:
        [dict] -- keys are the classification letter, values are the percent
                  score needed to achieve that class.
    """
    initial_dict = {}

    for classification in classification_dict:

        if 2.0 in initial_dict.values():
            break

        if classification == 'U':
            continue

        for n in np.arange(2.0, 100.0, 0.0001):
            if (
                ((score_sum + n) / (score_count + 1)
                 ) >= classification_dict[classification]
            ):
                initial_dict[classification] = round(n, 4)
                break

    return initial_dict
