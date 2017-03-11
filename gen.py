# coding=utf-8
import requests
import re
from lxml import etree
from urlparse import urljoin
from PIL import Image
from io import BytesIO


def login(session):
    """ Login a session to `http://cj.shu.edu.cn`
    Args:
        session: requests.Session
    Returns:
        result: True or False
    """
    start_url = 'http://cj.shu.edu.cn'
    start_req = session.get(start_url)
    tree = etree.HTML(start_req.text)

    # Get login form's fields
    login_fields = tree.xpath(r'//input[starts-with(@id, "txt")]/@id')

    # Get validate pic
    pic_src = tree.xpath(r'//img[@id="Img1"]/@src')[0]
    pic_url = urljoin(start_url, pic_src)
    pic_content = session.get(pic_url).content
    Image.open(BytesIO(pic_content)).show()

    # Load login data
    login_data = {key: raw_input('%s: ' % key) for key in login_fields}

    # Do login and check
    login_req = session.post(start_url, login_data)
    if login_req.url != start_req.url:
        return True

    # Get error info
    tree = etree.HTML(login_req.text)
    err_msg = tree.xpath(r'normalize-space(//div[@id="divLoginAlert"])')
    print err_msg
    return False


def get_term_data(session):
    """ Get term data
    Args:
        session: requests.Session
    Returns:
        term_data: list of (term_id, term_name)
    """
    start_url = 'http://cj.shu.edu.cn/StudentPortal/StudentSchedule'
    start_req = session.get(start_url)
    tree = etree.HTML(start_req.text)

    # Get term info
    term_elems = tree.cssselect(r'option')
    term_data = [(e.get('value'), e.text) for e in term_elems]
    return term_data


def get_course_table(session, term_id):
    """ Get course table data
    Args:
        session: requests.Session
        term_id: id of target term
    Returns:
        data: list course data
    """
    url = 'http://cj.shu.edu.cn/StudentPortal/CtrlStudentSchedule'
    data = {'AcademicTermID': term_id}
    req = session.post(url, data)
    tree = etree.HTML(req.text)

    # Get course data
    courses = tree.xpath(r'//table/tr[count(td)>9]')
    data = [[e.strip() for e in c.xpath(r'td/text()')] for c in courses]
    return data


def parse_time(text):
    """ Parse text to time
    Args:
        text: "二1-2 三4-5"
    Returns:
        time: [(2, 1, 2), (3, 4, 5)]
    """
    pattern = re.compile(ur'(?P<day>[一二三四五])(?P<from>\d+)-(?P<to>\d+)\b')
    data = pattern.findall(text)
    return [(u'#一二三四五'.index(i[0]), int(i[1]), int(i[2])) for i in data]


session = requests.Session()
if login(session):
    term_data = get_term_data(session)
    for i, term in enumerate(term_data):
        print '[%d] %s' % (i, term[1])
    op = input('Choose a term: ')
    data = get_course_table(session, term_data[op][0])

