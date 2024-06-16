from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("write please 10-digit number.")
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use please DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_record(self, record):
        self.contacts.append(record)

    def find(self, name):
        for contact in self.contacts:
            if contact.name.value == name:
                return contact
        return None

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Incomplete command. Input all necessary arguments."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def get_upcoming_birthdays(contacts, days=7):
    upcoming_birthdays = []
    today = datetime.today()
    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = contact.birthday.value.replace(year=today.year + 1)
            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() == 5: # субота
                    birthday_this_year += timedelta(days=2)
                elif birthday_this_year.weekday() == 6: # неділя
                    birthday_this_year += timedelta(days=1)

                upcoming_birthdays.append({"name": contact.name.value, "congratulation_date": birthday_this_year.strftime('%d.%m.%Y')})
    return upcoming_birthdays

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return ", ".join(phone.value for phone in record.phones)
    else:
        return "Contact not found."

@input_error
def show_all(book: AddressBook):
    if book.contacts:
        return "\n".join(contact.name.value + ": " + ", ".join(phone.value for phone in contact.phones) for contact in book.contacts)
    else:
        return "Address book is empty."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime('%d.%m.%Y')
    else:
        return "Birthday not found."

@input_error
def birthdays(_, book: AddressBook):
    upcoming_birthdays = get_upcoming_birthdays(book.contacts)
    if upcoming_birthdays:
        return "\n".join(contact["name"] + ": " + contact["congratulation_date"] for contact in upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")
    save_data(book) 
if __name__ == "__main__":
    main()