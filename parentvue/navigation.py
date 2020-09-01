from helium import *
import time


def login(url, username, password):
    start_chrome(url)

    # click to login as parent
    wait_until(Text('I am a parent').exists)
    click('I am a parent')

    # login
    wait_until(Button('Login').exists)
    write(username, into='User Name')
    write(password, into='Password')
    click('Login')

    # wait for greeting to show up on homepage
    wait_until(S("#Greeting").exists, 15)
    time.sleep(4)  # Add delay for page loading pane slowly


def schedule(url):
    go_to(url)
    # wait_until(Text("Bell Schedule").exists, 20)
    wait_until(Text("Term 1", to_right_of="Today").exists, 20)
    # wait_until(find_all(S("//*/span[contains(@data-bind, 'bellSchedName')]"))[0].exists, 20)


def gradebook_clicklink(link):
    classname = None
    if hasattr(link, "text"):
        classname = link.text
    click(link)
    wait_until(S(".card-row").exists, 20)
    wait_until(Text("Assignment View").exists, 10)
    click("Assignment View")
    wait_until(Text("Totals").exists, 20)
    return classname


def gradebook(url):
    go_to(url)
    wait_until(Text("Classes for ").exists, 20)

    # Go into first subject
    gradebook_clicklink(Button("1: "))


def gradebook_switchclass(url, current_class, classname=None, reverse=False, sort=False):
    # verify on the correct page
    if url is not None and url != get_driver().current_url:
        return

    # compare classname param
    if classname is not None and classname == current_class:
        # already on the correct class page
        return

    # click the dropdown button
    click((find_all(S("//*/div[contains(@data-bind, 'ClassesVisible')]/button[@class='btn dropdown-toggle']"
                      ))[0]).web_element)
    time.sleep(.5)

    # get class links from dropdown
    classlinks = find_all(S("//*/div[contains(@data-bind, 'ClassesVisible')]/ul/li/a[@href='#']"))
    # sort class links
    if sort:
        classlinks.sort(key=lambda x: x.web_element.text)

    # loop through class links and click matching or next
    for idx, link in enumerate(classlinks):
        if classname is not None:
            if link.web_element.text == classname:
                # click specific class in dropdown list
                return gradebook_clicklink(link.web_element)
        else:
            # find current class in class list dropdown
            if link.web_element.text == current_class:
                if reverse:
                    if idx > 0:
                        # click previous class in dropdown list
                        return gradebook_clicklink(classlinks[idx - 1].web_element)
                    else:
                        # at the beginning of list, can't do anything
                        return current_class
                else:
                    if idx < (len(classlinks) - 1):
                        # click next class in dropdown list
                        return gradebook_clicklink(classlinks[idx + 1].web_element)
                    else:
                        # at the end of list, can't do anything
                        return current_class
