import sys
import traceback
import time
from datetime import datetime
from pytz import timezone


def main():
    """
    args ./log_input/log.txt ./log_output/hosts.txt ./log_output/resources.txt ./log_output/hours.txt ./log_output/blocked.txt
    """
    hosts = open(sys.argv[2], 'w')
    resources = open(sys.argv[3], 'w')
    hours = open(sys.argv[4], 'w')
    blocked = open(sys.argv[5], 'w')
    events = open('../log_output/event-log.txt', 'w')
    error = open('../log_output/error-log.txt', 'w')
    warningshttp = open('../log_output/warning-protocol-log.txt', 'w')
    # Reads log file
    requests = open(sys.argv[1], 'r')
    try:
        print(time.strftime('[%Y-%m-%d %H:%M:%S%z]'), 'Initializing Analysis ')
        events.write(time.strftime('[%Y-%m-%d %H:%M:%S%z]') + 'Initializing Analysis \n')
        data_structure = Structure(requests, hosts, resources, hours, blocked)
        data_structure.generate_linked_list_hosts()
        data_structure.generate_linked_list_resources()
        data_structure.generate_linked_list_hours()
    except ValueError or IndexError or UnicodeEncodeError:
        tb = traceback.format_exc()
        print(tb)
        error.write(time.strftime('[%Y-%m-%d %H:%M:%S%z]') + ' Error reading file and during analysis \n')
        error.write(time.strftime('[%Y-%m-%d %H:%M:%S%z]') + str(tb))
    finally:
        print(time.strftime('[%Y-%m-%d %H:%M:%S%z]') + ' Analysis finalized. ')
        events.write(time.strftime('[%Y-%m-%d %H:%M:%S%z]') + ' Analysis finalized.  \n')


class Node:
    """
    Abstracts a basic node for the List
    """
    def __init__(self, value=None, domain=""):
        self.domain = domain
        self.next = None
        self.requests = value


class OrderedList:
    """
    Abstracts a sorted linked list with necessary data
    """
    def __init__(self):
        self.total_number_items_display = 9
        self.cursor = None
        self.beginning = None

    def insert_ordered_node(self, node):
        # move cursor to beginning of the list (to keep it ordered)
        self.cursor = self.beginning
        if self.beginning is None:
            """If no elements then initialize"""
            # Initialize cursor and starting point
            self.beginning = node
            self.cursor = node
        else:
            # If inserted node is the lower or same value
            # then point node->next to the beginning of the list.
            if self.beginning.requests <= node.requests:
                node.next = self.beginning
                self.beginning = self.cursor = node
            else:
                while self.cursor is not None:
                    # Iterate till the next node is null (last element).
                    # If next after cursor is None then point node being analyzed to it
                    if self.cursor.next is None:
                        self.cursor.next = node
                        break
                    else:
                        # keep asking till we find its position
                        if self.cursor.next.requests <= node.requests:
                            # save a temporary connection to the next node
                            node_temp = self.cursor.next
                            # place the node in its corresponded position
                            self.cursor.next = node
                            # attach temporary list to the next node
                            node.next = node_temp
                            break
                        else:
                            # move cursor to analyze next element (till it ends up in next == None)
                            self.cursor = self.cursor.next

    def print_list(self):
        return ''


class OrderListDomains(OrderedList):

    def print_list(self):
        # point cursor to the very beginning
        self.cursor = self.beginning
        i = 0
        string = ''
        while self.cursor is not None:
            # Iterate and print list
            string += '{},{}\n'.format(self.cursor.domain, self.cursor.requests)
            print('{},{}'.format(self.cursor.domain, self.cursor.requests))

            # move cursor to next item
            self.cursor = self.cursor.next
            i += 1
            if i > self.total_number_items_display:
                return string
        return string


class OrderListResources(OrderedList):

    def print_list(self):
        # point cursor to the very beginning
        self.cursor = self.beginning
        i = 0
        string = ''
        while self.cursor is not None:
            # Iterate and print list
            string += '{}\n'.format(self.cursor.domain)
            print('{}'.format(self.cursor.domain))


            # move cursor to next item
            self.cursor = self.cursor.next
            i += 1
            if i > self.total_number_items_display:
                return string
        return string


class OrderListHours(OrderedList):

    def print_list(self):
        # point cursor to the very beginning
        self.cursor = self.beginning
        i = 0
        string = ''
        while self.cursor is not None:

            date_event = datetime.fromtimestamp(self.cursor.domain, timezone('US/Eastern'))
            string += '{},{}\n'.format(date_event.strftime("%d/%b/%Y:%H:%M:%S -0400"), self.cursor.requests)
            print('{},{}'.format(date_event.strftime("%d/%b/%Y:%H:%M:%S -0400"), self.cursor.requests))
            # move cursor to next item
            self.cursor = self.cursor.next
            i += 1
            if i > self.total_number_items_display:
                return string
        return string


class Structure:
    """
    Stores Raw data into a dictionary.
    Data has been cleaned using iconv in run.sh
    @todo implement https://pypi.python.org/pypi/iconv/1.0 -  http://stackoverflow.com/a/38534992/4705437 - http://stackoverflow.com/a/10377179/4705437
    """
    ordered_linked_list_domains = OrderListDomains()
    ordered_linked_list_resources = OrderListResources()
    ordered_linked_list_hours = OrderListHours()
    hosts_hash = {}
    resources_hash = {}
    hours_hash = {}
    # temporary solution to avoid analyzing huge files
    times = 0

    def __init__(self, requests, hosts, resources, hours, blocked):
        """
        Reads file and generates dictionaries with data needed for custom Data Structures.
        :param requests:
        """
        self.hosts_file = hosts
        self.resources_file = resources
        self.blocked_file = blocked
        self.hours_file = hours
        self.blocked_counter = {}
        self.blocked_first_request = {}
        self.blocked_new_requests_from = {}
        self.blocked_last_request = {}
        self.hours_hash = {}

        for line in requests:
            try:
                row = line.split(" ")
                # @todo if array bigger than expected then skip and print into the error log.
                ip_name = row[0].replace(" ", "").lower()
                resource_name = self.clean_resource_url(self, row)
                row[-1] = row[-1].replace("\n", "")
                if ip_name == "":
                    # @todo regex valid IP address and domains if not match then send to error log:
                    # ^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])
                    # ([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$
                    print("Warning with this request: ", row)
                    continue

                # 1st feature.
                if ip_name not in self.hosts_hash:
                    self.hosts_hash[ip_name] = 1
                else:
                    self.hosts_hash[ip_name] += 1

                # 2nd feature.
                byts = 0 if row[-1] == '-' else int(row[-1])
                if resource_name not in self.resources_hash:
                    self.resources_hash[resource_name] = byts
                else:
                    self.resources_hash[resource_name] += byts

                # 4th feature.
                if ip_name not in self.blocked_new_requests_from:
                    # initialize requests for new IPs
                    self.blocked_new_requests_from[ip_name] = False

                if resource_name == '/login' and row[-2] == "401":
                    # Original request: ';;'.join(row[:6] + resource_name + row[-3:]
                    # Date format: 01/Jul/1995:00:00:12 -0400
                    # https://docs.python.org/3/library/time.html
                    # http://stackoverflow.com/questions/466345/converting-string-into-datetime
                    datetime_object = time.strptime(row[3][1:] + row[4][:-1], '%d/%b/%Y:%H:%M:%S%z')
                    timestamp = time.mktime(datetime_object)
                    if ip_name in self.blocked_counter:
                        if (timestamp - self.blocked_first_request[ip_name]) < 20:
                            # @todo avoid keep increasing counter
                            self.blocked_counter[ip_name] += 1
                            if self.blocked_counter[ip_name] == 3:
                                self.blocked_new_requests_from[ip_name] = True
                                self.blocked_last_request[ip_name] = timestamp
                    else:
                        # if brand new element then record it and record its time stamp
                        self.blocked_counter[ip_name] = 1
                        self.blocked_first_request[ip_name] = timestamp
                    # I need to keep track of:
                    # time of first request
                    # record requests after 20 seconds after first request
                    # reset time of first request after 20 seconds
                    # if requests are blocked
                    #
                    # I might need a dic with:
                    # - each request (and its ip_name)
                    # - a counter to see if this request was repeated more than 3 times in a timeframe of 20 mins
                    # - time of first request
                    # - field to keep track of five minutes after the third failed login request
                if (row[-2] != "401" or (ip_name in self.blocked_new_requests_from
                                         and self.blocked_new_requests_from[ip_name] is True)) \
                        and (ip_name in self.blocked_last_request and (
                            timestamp - self.blocked_last_request[ip_name]) <= 300) \
                        and ip_name in self.blocked_counter:
                    if self.blocked_counter[ip_name] > 3:
                        print(line)
                        self.blocked_file.write(line)
                elif (self.blocked_new_requests_from[ip_name] is True and
                        (timestamp - self.blocked_last_request[ip_name]) > 300) or \
                        (resource_name == '/login' and row[-2] == "200"):
                    if ip_name in self.blocked_counter:
                        del self.blocked_counter[ip_name]
                    if ip_name in self.blocked_new_requests_from:
                        del self.blocked_new_requests_from[ip_name]
                    if ip_name in self.blocked_last_request:
                        del self.blocked_last_request[ip_name]
                    if ip_name in self.blocked_first_request:
                        del self.blocked_first_request[ip_name]

                # 3rd feature
                current_date = line.split("[")[1].split("]")[0]
                date_event = datetime.strptime(current_date, "%d/%b/%Y:%H:%M:%S %z")
                timestamp = date_event.timestamp()
                if timestamp not in self.hours_hash:
                    self.hours_hash[timestamp] = 0
                for key in self.hours_hash:
                    # Computing intensive this will make the program take a long time if input is big.
                    c = timestamp - key
                    if c <= 3600.0:
                        self.hours_hash[key] += 1
                if self.times >= 2000:
                    break
                self.times += 1

            except UnicodeEncodeError:
                print('UnicodeEncodeError')
                # @todo send to log
                continue

    def generate_linked_list_hosts(self):
        """
        Generates ordered linked list and prints out values into hosts file
        :return: void
        """
        for domain, requests in self.hosts_hash.items():
            self.ordered_linked_list_domains.insert_ordered_node(Node(requests, domain))
        self.hosts_file.write(self.ordered_linked_list_domains.print_list())

    def generate_linked_list_resources(self):
        """
        Generates ordered linked list and prints out values into hosts file
        :return: void
        """
        for domain, resource in self.resources_hash.items():
            self.ordered_linked_list_resources.insert_ordered_node(Node(resource, domain))
        self.resources_file.write(self.ordered_linked_list_resources.print_list())

    def generate_linked_list_hours(self):
        """
        Generates ordered linked list and prints out values into hosts file
        :return: void
        """
        for domain, resource in self.hours_hash.items():
            self.ordered_linked_list_hours.insert_ordered_node(Node(resource, domain))
        self.hours_file.write(self.ordered_linked_list_hours.print_list())

    @staticmethod
    def clean_resource_url(self, line):
        """
        Analyzing the log file and instructions we are expected to have 5 columns with valid data.
        This log is similar to a common/access log
        http://publib.boulder.ibm.com/tividd/td/ITWSA/ITWSA_info45/en_US/HTML/guide/c-logs.html#common
        https://www.w3.org/Protocols/HTTP/1.0/spec.html
        https://tools.ietf.org/html/rfc7230
        http://www.juniper.net/techpubs/en_US/webapp5.6/topics/reference/w-a-s-ap-mp-missing-http-protocol.html
            HTTP version different to HTTP/1.0, HTTP/0.9 or HTTP/1.1 are send to log file

        Turns out requested resources (URLs) might have weird characters and even blank spaces on them
        Since it's "users' input" data this function tries to amend them.
        @todo clean them at the run.sh level using awk

        :param line:
        :return:
        """
        resource = ''
        # found = False
        for l in line[6:-2]:
            # Warning assuming we have two columns at the end of the line.
            if l.startswith('HTTP/1.0', 0, 8) or l.startswith('HTTP/0.9', 0, 8) or l.startswith('HTTP/1.1', 0, 8):
                found = True
                break
            resource += l.replace(" ", "").replace("\"", "").lower()
        # if found is False:
            # print("Warning: line does not have HTTP protocol version", line)
            # Skip line and report
        return resource

if __name__ == '__main__':
    main()



