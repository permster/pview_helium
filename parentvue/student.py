import re
from helium import *
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from parentvue import navigation


def set_query_parameter(url, param_name, param_value):
    # Given a URL, set or replace a query parameter and return the modified URL.

    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    if param_value is None and query_params[param_name]:
        # remove the param from query
        del query_params[param_name]
    else:
        query_params[param_name] = [param_value]

    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def get_students():
    student_list = []
    students = find_all(S("//*/div[@class='student']/h2"))
    for s in students:
        student_list.append(Student(s.web_element.text))
    return student_list


def get_current_class():
    # get current class name
    return (find_all(S("//*/div/button[contains(@data-bind,'SelectedClassName')]"))[0]).web_element.text


def get_table_data(div_column='headers', div_row='rowsview'):
    columns = []
    column_headers = []

    headers = find_all(S(f"//*/div[contains(@class, '{div_column}')]/div/table/tbody/tr/td"))
    for header in headers:
        column_headers.append(header.web_element.text)

    column_count = int((find_all(S(f"//*/div[contains(@class, '{div_column}')]/div/table/tbody/tr/td[not("
                                   f"@aria-colindex <= preceding-sibling::td/@aria-colindex) and "
                                   f"not(@aria-colindex <=following-sibling::td/@aria-colindex)]")
                                 ))[0].web_element.get_attribute('aria-colindex'))

    for idx in range(1, column_count + 1):
        column_cells = find_all(S(f"//*/div[contains(@class, '{div_row}')]/div/table/tbody/tr/"
                                  f"td[@aria-colindex='{idx}']"))
        columns.append([cell.web_element.text for cell in column_cells])

    data = list(zip(*columns))
    data.insert(0, tuple(column_headers))
    return data


class Student(object):

    def __init__(self, name, **kwargs):
        super(Student, self).__init__()
        self.name = name
        self.id = self.school = self.image = self.agu = None
        self.classlist = self.grades = self.schooldistrict = None
        self.link_gradebook = self.link_classlist = None

        if len(kwargs) > 0:
            self._build(kwargs)
        else:
            self.get_id()
            self.get_agu()
            self.get_image()
            self.get_school()
            self.get_schooldistrict()
            self.get_link_classlist()
            self.get_link_gradebook()

    def _build(self, data):
        """Build our this :class:`Student` object"""
        for key, val in data.items():
            setattr(self, key, val)

    def get_id(self):
        self.id = ((find_all(S(f"//*/div[@class='student']/h2[text()='{self.name}']/following-sibling"
                               f"::div[@class='info']")
                             )[0].web_element.text.splitlines()[0]).strip()).strip("ID: ")

    def get_agu(self):
        # //*/div[@class='student']/h2[text()='Jonathan']/ancestor::div[@data-agu]
        # //*/form/*/div[@data-agu]/@data-agu
        # f"//*/div[@class='student']/h2[text()='{self.name}']/ancestor::div[@data-agu]"
        self.agu = (find_all(S(f"//*/div[@class='student']/h2[text()='{self.name}']/ancestor::div[@data-agu]")
                             )[0]).web_element.get_attribute('data-agu')

    def get_school(self):
        self.school = ((find_all(S(f"//*/div[@class='student']/h2[text()='{self.name}']/following-sibling"
                                   f"::div[@class='info']")
                                 )[0]).web_element.text.splitlines()[1]).strip()

    def get_schooldistrict(self):
        self.schooldistrict = (find_all(S("#DistrictName"))[0]).web_element.text

    def get_image(self):
        # xPath only works on homepage, may want to switch to using student-photo instead from dropdown <li>
        self.image = (find_all(S(f"//*/div[@class='student-image']/img[@alt='{self.name}']")
                               )[0]).web_element.get_attribute('src')

    def get_classlist(self):
        navigation.schedule(self.link_classlist)

        classnames = []
        cells = find_all(S(f"//*/ul[@class='list-group layout-table padded']/li"))
        for cell in cells:
            classnames.append(re.search(".*\d\s(.*)\s\-\s\d.*", cell.web_element.text.split('\n', 1)[0]).group(1))
        self.classlist = classnames

    def get_class(self, classname, **kwargs):
        xPath = ""

    def get_link_classlist(self):
        # set AGU param in query
        self.link_classlist = set_query_parameter(Link('Class Schedule').href, "AGU", self.agu)

    def get_link_gradebook(self):
        # set AGU param in query
        gradebook = set_query_parameter(Link('Grade Book').href, "AGU", self.agu)

        # remove studentGU param from grade book link
        self.link_gradebook = set_query_parameter(gradebook, "studentGU", None)

    def get_grades(self, **kwargs):
        # get_classlist may need to be called prior to running this function
        navigation.gradebook(self.link_gradebook)
        class_list = [get_current_class()]
        grades = [get_table_data()]

        # get grade data from table
        while navigation.gradebook_switchclass(self.link_gradebook, class_list[-1]) != class_list[-1]:
            class_list.append(get_current_class())

            # append grade data to list
            grades.append(get_table_data())

        self.grades = dict(zip(class_list, grades))
