#! /Users/sechilds/anaconda3/envs/presto_scrape/bin/python
# coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
from delorean import Delorean
from delorean import parse
from secrets import library_card, library_pin
from time import sleep

def main():
    tz = 'US/Eastern'

    driver = webdriver.Firefox()

    driver.get('https://torontopubliclibrary.ca/signin')
    card_no = driver.find_element_by_id('userId')
    card_no.send_keys(library_card)
    password_box = driver.find_element_by_id('password')
    password_box.send_keys(library_pin)
    submit_button = driver.find_element_by_class_name('signin')
    submit_button.click()

    #driver.get('https://account.torontopubliclibrary.ca/')
    driver.get('https://account.torontopubliclibrary.ca/checkouts')
    sleep(3)
    item_table = driver.find_element_by_class_name('item-list')
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
            how_long = item_date_due - Delorean(timezone = tz)
            item_name = cells[2].text
            print(f'{item_title} by {item_author} is due in {how_long.days} days on {item_due}')
        except IndexError:
            pass

    # the problem with holds - there are 3 tables:
    # holds-redux still-on-hold
    # holds-redux in-transit
    # what's the 3rd one??? Until I see it -- I can't really look for it.
    driver.get('https://account.torontopubliclibrary.ca/holds')
    sleep(3)
    # books in transit
    in_transit = driver.find_element_by_class_name('in_transit')
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
            print(f'Hold on {item_title} by {item_author} is in transit.')
        except IndexError:
            pass
    # look at those still on hold
    still_on_hold = driver.find_element_by_class_name('still-on-hold')
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
            print(f'Hold on {item_title} by {item_author} is {item_status}. Position: {item_position}.')
            # item_date_due = parse(item_due, timezone = tz)
            # how_long = item_date_due - Delorean(timezone = tz)
            #item_name = cells[2].text
            #print(f'{item_title} by {item_author} is due in {how_long.days} days on {item_due}')
            #print(cells)
        except IndexError:
            pass

    driver.close()

if __name__ == "__main__":
    main()

