#! /Users/sechilds/anaconda3/envs/presto_scrape/bin/python
# coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from delorean import Delorean
from delorean import parse
from secrets import library_card, library_pin
from time import sleep
from datetime import timedelta

def remove_non_ascii(s):
    return ''.join([i if ord(i) < 128 else ' ' for i in s])

def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(remove_non_ascii(s))

def main():
    tz = 'US/Eastern'

    l = [] # collect data in list

    driver = webdriver.Firefox(log_path = '/Users/sechilds/geckodriver.log')

    driver.get('https://torontopubliclibrary.ca/signin')
    card_no = driver.find_element_by_id('userId')
    card_no.send_keys(library_card)
    password_box = driver.find_element_by_id('password')
    password_box.send_keys(library_pin)
    submit_button = driver.find_element_by_class_name('signin')
    submit_button.click()

    driver.get('https://account.torontopubliclibrary.ca/checkouts')
    sleep(3)
    try:
        item_table = driver.find_element_by_class_name('item-list')
    except NoSuchElementException:
        item_table = False
    if item_table:
        html_table = item_table.get_attribute('outerHTML')
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = soup.findAll("tr")

        for row in rows:
            cells = row.find_all('td')
            try:
                item_due = cells[3].text
                item_parts = cells[2].find_all('div')
                item_title = item_parts[0].text
                item_author = item_parts[1].text
                item_date_due = parse(item_due, timezone = tz)
                how_long = item_date_due - Delorean(timezone = tz) + timedelta(days=1)
                day_text = ('1 day' if how_long.days == 1 else f'{how_long.days} days')
                item_name = cells[2].text
                l.append(f'{how_long.days}D: {item_title} by {item_author} is due in {day_text} on {item_due}')
            except IndexError:
                pass

    # the problem with holds - there are 3 tables:
    # holds-redux still-on-hold
    # holds-redux in-transit
    # holds-redux ready-for-pickup
    # what's the 3rd one??? 
    driver.get('https://account.torontopubliclibrary.ca/holds')
    sleep(3)
    # books ready for pickup
    try:
        ready_for_pickup = driver.find_element_by_class_name('ready-for-pickup')
    except NoSuchElementException:
        ready_for_pickup = False
    if ready_for_pickup:
        item_table = ready_for_pickup.find_element_by_class_name('item-list')
        html_table = item_table.get_attribute('outerHTML')
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = soup.findAll("tr")

        for row in rows:
            cells = row.find_all('td')
            try:
                #item_due = cells[5].find_all('div')
                hold_due = cells[5]
                hold_due_date = list(hold_due.stripped_strings)[1]
                hold_date_due = parse(hold_due_date, timezone = tz)
                item_parts = cells[2].find_all('div')
                #for i, item in enumerate(cells):
                #    print(f'part {i}: {item.text}')
                #for i, item in enumerate(item_due):
                #    print(f'part {i}: {item.text}')
                item_title = item_parts[0].text
                item_author = item_parts[1].text
                how_long = hold_date_due - Delorean(timezone = tz) + timedelta(days=1)
                hold_day_text = ('1 day' if how_long.days == 1 else f'{how_long.days} days')
                l.append(f'Hold on {item_title} by {item_author} is in ready for pickup. Pick up by {hold_date_due.format_datetime()} ({hold_day_text})')
            except IndexError:
                pass
    # books in transit
    try:
        in_transit = driver.find_element_by_class_name('in-transit')
    except NoSuchElementException:
        in_transit = False
    if in_transit:
        item_table = in_transit.find_element_by_class_name('item-list')
        html_table = item_table.get_attribute('outerHTML')
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = soup.findAll("tr")

        for row in rows:
            cells = row.find_all('td')
            try:
                item_due = cells[3].text
                item_parts = cells[2].find_all('div')
                #for i, item in enumerate(cells):
                #    print(f'part {i}: {item.text}')
                item_title = item_parts[0].text
                item_author = item_parts[1].text
                l.append(f'Hold on {item_title} by {item_author} is in transit.')
            except IndexError:
                pass
    # look at those still on hold
    try:
        still_on_hold = driver.find_element_by_class_name('still-on-hold')
    except NoSuchElementException:
        still_on_hold = False
    if still_on_hold:
        item_table = still_on_hold.find_element_by_class_name('item-list')
        html_table = item_table.get_attribute('outerHTML')
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = soup.findAll("tr")

        for row in rows:
            cells = row.find_all('td')
            try:
                item_due = cells[3].text
                item_parts = cells[2].find_all('div')
                #for i, item in enumerate(cells):
                #    print(f'part {i}: {item.text}')
                item_title = item_parts[0].text
                item_author = item_parts[1].text
                item_position = cells[3].text
                item_status = cells[5].text
                l.append(f'Hold on {item_title} by {item_author} is {item_status}. Position: {item_position}.')
                # item_date_due = parse(item_due, timezone = tz)
                # how_long = item_date_due - Delorean(timezone = tz)
                #item_name = cells[2].text
                #print(f'{item_title} by {item_author} is due in {how_long.days} days on {item_due}')
                #print(cells)
            except IndexError:
                pass

    driver.close()
    s = 'Next: '
    if  item_table:
        s += f'Due: {day_text}'
    if ready_for_pickup:
        s += f'Holds: {day_text}'

    if item_table or ready_for_pickup:
        safe_print(s)
    else:
        safe_print('Nothing Due or Ready for Pickup')

    for line in l:
        safe_print(line)


if __name__ == "__main__":
    main()

