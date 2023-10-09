from collections import UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(phone):
        return len(phone) == 10 and phone.isdigit()

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid_phone(new_value):
            raise ValueError("Invalid phone number format")
        self._value = new_value

class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, '%Y-%m-%d')
            self._value = new_value
        except ValueError:
            raise ValueError("Invalid birthday date format. Use YYYY-MM-DD format.")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        found = False
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break
        else:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = datetime(today.year, self.birthday.month, self.birthday.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.month, self.birthday.day).date()
            days_until_birthday = (next_birthday - today).days
            return days_until_birthday
        return None

    def __str__(self):
        birthday_info = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_info}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self._values = []

    def add_record(self, record):
        self.data[record.name.value] = record
        self._values.append(record)

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self._values = [record for record in self._values if record.name.value != name]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._values):
            result = self._values[self._index]
            self._index += 1
            return result
        raise StopIteration
    
    def __str__(self):
        return "\n".join([str(record) for record in self._values])

    def paginated_list(self, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        return self._values[start:end]

class Assistant:
    def __init__(self):
        self.contacts = AddressBook()

    def run(self):
        print("Bot assistant is running. Type 'exit' to exit.")
        while True:
            command = input("Enter a command: ")
            try:
                result = self.parse_command(command)
                if result:
                    print(result)
            except Exception as e:
                print(f"Error: {str(e)}")

    def parse_command(self, command):
        command = command.lower()
        if command == 'hello':
            return "How can I help you?"
        elif command.startswith('add '):
            _, data = command.split(' ', 1)
            parts = data.split()
            if len(parts) != 3:
                return "Give me name, phone, and birthday (if applicable)"
            name, phone, birthday = parts
            self.contacts.add_record(Record(name, birthday))
            self.contacts.data[name].add_phone(phone)
            return f"Added contact: {name}, {phone}, Birthday: {birthday}"
        elif command.startswith('change '):
            _, data = command.split(' ', 1)
            if ' ' not in data:
                return "Give me name and phone please"
            name, phone = data.split()
            contact = self.contacts.find(name)
            if contact:
                contact.edit_phone(contact.phones[0].value, phone)
                return f"Updated contact: {name}, {phone}"
            else:
                raise ValueError(f"Contact '{name}' not found.")
        elif command.startswith('phone '):
            _, name = command.split(' ', 1)
            contact = self.contacts.find(name)
            if contact:
                return f"Phone number for {name}: {contact.phones[0].value}"
            else:
                raise ValueError(f"Contact '{name}' not found.")
        elif command == 'show all':
            if not self.contacts.data:
                return "No users found"
            return self.paginated_contacts(page=1, page_size=5)
        elif command.startswith('show page '):
            _, page_str = command.split(' ', 2)
            try:
                page = int(page_str)
                if page <= 0:
                    raise ValueError("Page number must be a positive integer.")
                return self.paginated_contacts(page, page_size=5)
            except ValueError:
                return "Invalid page number."
        elif command in ['good bye', 'close', 'exit']:
            print("Good bye!")
            exit()
        elif command in ['add', 'change']:
            return "Give me name and phone please"
        elif command == 'phone':
            return "Give me name please"
        else:
            raise ValueError("Unknown command.")

    def paginated_contacts(self, page, page_size):
        contacts = self.contacts.paginated_list(page, page_size)
        if not contacts:
            return "No contacts found on this page."
        return "\n".join([str(record) for record in contacts])

if __name__ == "__main__":
    bot = Assistant()
    bot.run()
