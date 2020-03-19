from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

class ClassifactionWhatIf:
    """
    Use this object to get percent shooter needs in mext classifier to move up in classification.

    User methods -

    get_upped: returns the percent needed in next classifier to move up in classification.
    get_shooter_class: returns the shooter current classification.
    get_next_class: returns the next class up from the shooters current class.
    get_initial_classifaction: returns percent and class for a shooter to receive and inital classification.

    """

    def __init__(self, mem_num, division):
        """Takes shooters membership number and division to query and init the object and varibles"""

        self.mem_num = mem_num
        self.division = division.title() if division != 'PCC' else division.upper()
        self.division_search = division.title().replace(' ', '_') if division != 'PCC' else division.upper().replace(' ', '_')

        self.classification_dict = {'GM': 95, 'M': 85, 'A': 75, 'B': 60, 'C': 40, 'D': 2, 'U': 0}
        self.next_class_up = {'M':'GM', 'A':'M', 'B':'A', 'C':'B', 'D':'C'}
        self.reverse_classification_dict = {95:'GM', 85:'M', 75:'A', 60:'B', 40:'C', 2:'D', 0:'U'}

        division_list = ['Open', 'Limited', 'Limited 10', 'Production', 'Revolver', 'Single Stack', 'Carry Optics', 'PCC']
        if not self.division in division_list:
            raise ValueError(self.division + ' not a valid division')

        uspsa_org_response = urlopen(Request('https://uspsa.org/classification/' + self.mem_num, headers={'User-Agent': 'Chrome/80.0.3987.132'}))
        self.bs = BeautifulSoup(uspsa_org_response.read(), 'lxml')

        if self.bs.find('tbody', {'id':self.division_search + '-dropDown'}) is None:
            raise AttributeError('No records available for ' + self.mem_num + ' in ' + self.division + '.')



    def __get_classifier_scores(self):
        """Returns a list of tuples with the qualifying classifier scores"""

        self.classifier_score_list = []

        table_body = self.bs.find('tbody', {'id':self.division_search + '-dropDown'})
        table_rows = table_body.find_all('tr')

        for row in table_rows[1:]:
            if str(row.find_all('td')[3].text.strip()) == 'Y':
                self.classifier_score_list.append((str(row.find_all('td')[3].text.strip()), float(str(row.find_all('td')[4].text.strip()))))

        return self.classifier_score_list



    def __get_shooter_classifaction(self):
        """Returns classifacation for shooter in specified division"""

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
                self.classifacation = float(str([x.text.strip() for x in data][1].split(': ')[1]))

                return self.classifacation

        return None



    def get_upped(self):
        """Take classifier score list and current classifiaction percent, return percent needed on next classifier to class-up."""

        self.score_list = self.__get_classifier_scores()
        self.cur_pct = self.__get_shooter_classifaction()
        self.shooter_class = self.get_shooter_class()

        score_sum, score_count = self.__sum_scores()

        if self.shooter_class == 'U':
            return None

        return round((self.classification_dict[self.next_class_up[self.shooter_class]] * (score_count + 1)) - score_sum, 4)



    def get_shooter_class(self):
        """Return the shooters current classifaction letter."""

        self.cur_pct = self.__get_shooter_classifaction()
        self.shooter_class = 'U'

        if self.cur_pct >= self.classification_dict['GM']:
            self.shooter_class = 'GM'

        elif self.cur_pct >= self.classification_dict['M'] and self.cur_pct < self.classification_dict['GM']:
            self.shooter_class = 'M'

        elif self.cur_pct >= self.classification_dict['A'] and self.cur_pct < self.classification_dict['M']:
            self.shooter_class = 'A'

        elif self.cur_pct >= self.classification_dict['B'] and self.cur_pct < self.classification_dict['A']:
            self.shooter_class = 'B'

        elif self.cur_pct >= self.classification_dict['C'] and self.cur_pct < self.classification_dict['B']:
            self.shooter_class = 'C'

        elif self.cur_pct >= self.classification_dict['D'] and self.cur_pct < self.classification_dict['C']:
            self.shooter_class = 'D'


        return self.shooter_class



    def get_next_class(self):
        """Return the next class letter above the shooters current class."""

        self.shooter_class = self.get_shooter_class()

        if self.shooter_class == 'U':
            return 'U'

        return self.next_class_up[self.shooter_class]



    def get_initial_classifaction(self):
        """Take list of tuples with scores and return the initial class and percent needed for a 'U' shooter to get classified."""

        self.initial_classification = 'U'
        self.score_list = self.__get_shooter_classifaction()

        score_sum, score_count = self.__sum_scores()

        if round((self.classification_dict['GM'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['GM'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['GM']]

        if round((self.classification_dict['M'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['M'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['M']]

        if round((self.classification_dict['A'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['A'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['A']]

        if round((self.classification_dict['B'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['B'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['B']]

        if round((self.classification_dict['C'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['C'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['C']]

        if round((self.classification_dict['D'] * (score_count + 1)) - score_sum, 4) <= 100:
            return round((self.classification_dict['D'] * (score_count + 1)) - score_sum, 4), self.reverse_classification_dict[self.classification_dict['D']]

        return self.initial_classification


    def __sum_scores(self):
        """Private method used to provide a sum of the classifier scores"""

        self.score_list = self.__get_classifier_scores()
        self.score_sum = 0
        self.score_count = 0

        for score in self.score_list:
            if self.score_count < 5:
                self.score_sum += score[1]
                self.score_count += 1

        return self.score_sum, self.score_count
