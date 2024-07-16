from colectica_api import ColecticaObject
import pprint

def main():
    pp = pprint.PrettyPrinter(depth=4)

    hostname = "example.ucl.ac.uk"
    username = 'me@example.com'
    password = 'mypassword'

    C = ColecticaObject(hostname, username, password)

    pp.pprint(C.get_item_json('uk.alspac', '2f2d8823-2595-4adf-8347-147c9d7b81c8'))


if __name__ == "__main__":
    main()