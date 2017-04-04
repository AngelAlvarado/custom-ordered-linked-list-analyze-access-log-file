import sys
import traceback


def main():
    """
    args ./log_input/log.txt ./log_output/hosts.txt ./log_output/hours.txt ./log_output/resources.txt ./log_output/blocked.txt
    """
    hosts = open(sys.argv[2], 'w')
    hours = open(sys.argv[3], 'w')
    resources = open(sys.argv[4], 'w')
    blocked = open(sys.argv[5], 'w')
    # Reads log file
    requests = open(sys.argv[1], 'r')
    try:
        data_structure = Structure(requests, hosts, resources)
        data_structure.generate_linked_list_hosts()
        data_structure.generate_linked_list_resources()
    except ValueError or IndexError or UnicodeEncodeError:
        tb = traceback.format_exc()
        print(tb)
        print("Error reading file...")
        # @todo send date and message to log file
    finally:
        print('done')
        # @todo send date and message to log file


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
        self.total_number_items_display = 11
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
                    # Iterate till the next node is null (last element). If next after cursor is None then point node being analyzed to it
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


class Structure:
    """
    Stores Raw data into a dictionary.
    Data has been cleaned using iconv in run.sh
    @todo implement https://pypi.python.org/pypi/iconv/1.0 -  http://stackoverflow.com/a/38534992/4705437 - http://stackoverflow.com/a/10377179/4705437
    """
    ordered_linked_list_domains = OrderedList()
    ordered_linked_list_resources = OrderedList()
    hosts_hash = {}
    resources_hash = {}

    def __init__(self, requests, hosts, resources):
        """
        Reads file and generates dictionaries with data needed for custom Data Structures.
        :param requests:
        """
        self.hosts_file = hosts
        self.resources_file = resources

        for line in requests:
            try:
                row = line.split(" ")
                # @todo if array bigger than expected then skip and print into the error log.
                ip_name = row[0].replace(" ", "").lower()
                resource_name = self.clean_resource_url(row)
                if ip_name == "":
                    # @todo regex valid IP address and domains if not match then send to error log:
                    # ^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])
                    # ([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$
                    print("Warning with this request: ", row)
                    continue
                if ip_name not in self.hosts_hash:
                    self.hosts_hash[ip_name] = 1
                else:
                    self.hosts_hash[ip_name] += 1

                byts = 0 if row[-1] == '-' or row[-1] == '-\n' else int(row[-1])
                if resource_name not in self.resources_hash:
                    self.resources_hash[resource_name] = byts
                else:
                    self.resources_hash[resource_name] += byts

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

    def clean_resource_url(self, line):
        """
        Turns out requested resources (URLs) might have weird characters and even blank spaces on them
        Since it's "users' input" data this function tries to amend them.
        @todo clean this at the run.sh level(using awk)
        :param line:
        :return:
        """
        resource = ''
        for l in line[6:]:
            if l.startswith('HTTP/1.0', 0, 8):
                return resource
            resource += l.replace(" ", "").lower()


    def sort_using_dictionary(self):
        """
        @deprecated
        Temporary solution using collections ~ dictionaries
        # from collections import defaultdict
        # hosts_hash = defaultdict(int)
        :return: print 10 fist elements to stdout
        """
        i = 0
        for w in sorted(self.hosts_hash, key=self.hosts_hash.get, reverse=True):
            print(w, ',', self.hosts_hash[w])
            i += 1
            if i > 9:
                return

    def keying_hosts_list(self):
        """
        @deprecated
        Not using regular dics.
        :return:
        """
        for k, v in self.hosts_hash.items():
            self.number_requests.append(v)
            self.keyed_request_number_hash[v] = k

    def order_quick_sort(self, num_request):
        """
        @deprecated: it will get tricky to sort a list
        (with the total number of requests) and match its metadata(e.g. domain) later on.

        Note it's possible to use the built-in sorted() method.
        The sorting method is implemented since it's basically a requirement.

        """
        if len(num_request) < 2:
            return num_request
        else:
            pivot = num_request[0]
            lower = [i for i in num_request[1:] if i <= pivot]
            greater = [i for i in num_request[1:] if i > pivot]
            return self.order_quick(lower) + [pivot] + self.order_quick(greater)


if __name__ == '__main__':
    main()



