import requests
from bs4 import BeautifulSoup


classification_dict = {
    'GM': 95, 'M': 85, 'A': 75, 'B': 60, 'C': 40, 'D': 2, 'U': 0
}
next_class_up = {
    'M': 'GM', 'A': 'M', 'B': 'A', 'C': 'B', 'D': 'C'
}
reverse_classification_dict = {
    95: 'GM', 85: 'M', 75: 'A', 60: 'B', 40: 'C', 2: 'D', 0: 'U'
}
division_list = [
    'Open', 'Limited', 'Limited 10', 'Production',
    'Revolver', 'Single Stack', 'Carry Optics', 'PCC'
]


class ClassifactionWhatIf:

    """Use this object to get percent a shooter needs in mext classifier to
    move up in classification.

    Methods - get_upped, get_shooter_class, get_next_class,
    get_initial_classifaction"""

    def __init__(self, mem_num, division):
        """Args:
        mem_num -- shooters USPSA number as string object
        division -- shooters division as string object
        """

        self.mem_num = mem_num

        if division != 'PCC':
            self.division = division.title()
        else:
            self.division = division.upper()

        if self.division != 'PCC':
            self.division_search = division.title().replace(' ', '_')
        else:
            self.division_search = division.upper().replace(' ', '_')

        if self.division not in division_list:
            raise ValueError(f'{self.division} is not a valid division')

        uspsa_org_response = requests.get(
            f'https://uspsa.org/classification/{self.mem_num}'
        )
        self.bs = BeautifulSoup(uspsa_org_response.text, 'lxml')

        if (
            self.bs.find(
                'tbody', {'id': f'{self.division_search}-dropDown'}) is None
        ):
            raise AttributeError(
                f'No records available for {self.mem_num} in {self.division}.'
            )

    def __get_classifier_scores(self):
        """Returns a generator for the qualifying classifier scores"""

        table_body = self.bs.find(
            'tbody', {'id': f'{self.division_search}-dropDown'}
        )
        table_rows = table_body.find_all('tr')

        for row in table_rows[1:]:
            if str(row.find_all('td')[3].text.strip()) == 'Y':
                yield (
                    str(row.find_all('td')[3].text.strip()),
                    float(str(row.find_all('td')[4].text.strip()))
                )

    def __get_shooter_classifaction(self):
        """Returns classifacation for shooter in specified division or None"""

        table_body = self.bs.find_all('tbody')[2]
        rows = table_body.find_all('tr')

        for row in rows:
            header = row.find_all('th')
            data = row.find_all('td')

            try:
                float(str([x.text.strip() for x in data][1].split(': ')[1]))
            except ValueError:
                raise ValueError()

            if [x.text.strip() for x in header][0] == self.division:
                self.classifacation = (
                    float(
                        str([x.text.strip() for x in data][1].split(': ')[1]))
                )
                return self.classifacation

        return None

    def get_upped(self):
        """Returns percent needed on next classifier to class-up."""

        self.cur_pct = self.__get_shooter_classifaction()
        self.shooter_class = self.get_shooter_class()
        score_sum, score_count = self.__sum_scores()

        if self.shooter_class == 'U':
            return None
        return (
            round((classification_dict[next_class_up[self.shooter_class]]
                   * (score_count + 1)) - score_sum, 4)
        )

    def get_shooter_class(self):
        """Returns the shooters current classifaction letter."""

        self.cur_pct = self.__get_shooter_classifaction()
        self.shooter_class = 'U'

        if self.cur_pct >= classification_dict['GM']:
            self.shooter_class = 'GM'
        elif (
            self.cur_pct >= classification_dict['M'] and
            self.cur_pct < classification_dict['GM']
        ):
            self.shooter_class = 'M'
        elif (
            self.cur_pct >= classification_dict['A'] and
            self.cur_pct < classification_dict['M']
        ):
            self.shooter_class = 'A'
        elif (
            self.cur_pct >= classification_dict['B'] and
            self.cur_pct < classification_dict['A']
        ):
            self.shooter_class = 'B'
        elif (
            self.cur_pct >= classification_dict['C'] and
            self.cur_pct < classification_dict['B']
        ):
            self.shooter_class = 'C'
        elif (
            self.cur_pct >= classification_dict['D'] and
            self.cur_pct < classification_dict['C']
        ):
            self.shooter_class = 'D'

        return self.shooter_class

    def get_next_class(self):
        """Returns the next class letter above the shooters current class."""

        self.shooter_class = self.get_shooter_class()
        if self.shooter_class == 'U':
            return 'U'
        return next_class_up[self.shooter_class]

    def get_initial_classifaction(self):
        """Returns the initial class and percent needed for a 'U' shooter to
           get classified."""

        self.initial_classification = 'U'

        score_sum, score_count = self.__sum_scores()

        if (
            round((classification_dict['GM'] * (score_count + 1))
                  - score_sum, 4) <= 100
        ):
            return (
                round((classification_dict['GM'] * (score_count + 1))
                      - score_sum, 4),
                reverse_classification_dict
                [classification_dict['GM']]
            )

        if (
            round((classification_dict['M'] * (score_count + 1))
                  - score_sum, 4) <= 100
        ):
            return (
                round((classification_dict['M'] *
                       (score_count + 1)) - score_sum, 4),
                reverse_classification_dict[classification_dict['M']]
            )

        if (
            round((classification_dict['A'] *
                   (score_count + 1)) - score_sum, 4) <= 100
        ):
            return (
                round((classification_dict['A'] *
                       (score_count + 1)) - score_sum, 4),
                reverse_classification_dict[classification_dict['A']]
            )

        if (
            round((classification_dict['B'] *
                   (score_count + 1)) - score_sum, 4) <= 100
        ):
            return (round((classification_dict['B'] * (score_count + 1))
                          - score_sum, 4),
                    reverse_classification_dict[classification_dict['B']])

        if (
            round((classification_dict['C'] *
                   (score_count + 1)) - score_sum, 4) <= 100
        ):
            return (
                round((classification_dict['C'] *
                       (score_count + 1)) - score_sum, 4),
                reverse_classification_dict[classification_dict['C']]
            )

        if (
            round((classification_dict['D'] *
                   (score_count + 1)) - score_sum, 4) <= 100
        ):
            return (round((classification_dict['D'] * (score_count + 1))
                          - score_sum, 4),
                    reverse_classification_dict[classification_dict['D']])

        return self.initial_classification

    def __sum_scores(self):
        """Returns sum of the classifier scores and count of scores on
        record."""

        self.score_sum = 0
        self.score_count = 0

        for score in self.__get_classifier_scores():
            if self.score_count < 5:
                self.score_sum += score[1]
                self.score_count += 1

        return self.score_sum, self.score_count
