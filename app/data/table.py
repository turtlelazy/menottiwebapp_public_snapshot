def list_to_string(lst):
    return "(" + ", ".join(lst) + ")"


def add_type(field_name):
    return f"{field_name} TEXT"

def add_other_types(field_name, field_type):
    return f"{field_name} {field_type}"


def get_question_mark(thing):
    return "?"


def first(lst):
    return lst[0]


class Table:
    def __init__(self, db, table_name, search_field):
        self.db = db
        self.table_name = table_name
        self.search_field = search_field
        self.c = db.cursor()

    def add_values(self, values):
        "adds a row filled with values"
        question_marks = map(get_question_mark, values)
        value_string = list_to_string(question_marks)
        self.c.execute(
            f"INSERT INTO {self.table_name} VALUES {value_string}", values)
        self.db.commit()
    
    def drop(self):
        self.c.execute(
            f"DROP TABLE IF EXISTS {self.table_name}"
        )
        self.db.commit()

    def get_field(self, search_type):
        self.c.execute(
            f"SELECT {search_type} FROM {self.table_name}")

        value_lists = self.c.fetchall()
        return map(first, value_lists)

    def set_value(self, search, field, value):
        "sets field of a row with a search_field of search to value"
        self.c.execute(
            f"UPDATE {self.table_name} SET {field} = ? WHERE {self.search_field} = ?", [value, search])
        self.db.commit()

    def get_main_values(self):
        "returns a list of main fields"
        self.c.execute(f"SELECT {self.search_field} FROM {self.table_name}")
        value_lists = self.c.fetchall()
        return map(first, value_lists)

    def get_value_list(self, search, field):
        self.c.execute(
            f"SELECT {field} FROM {self.table_name} WHERE {self.search_field} = ?", [search])
        return self.c.fetchone()

    def get_search_list(self, search, field, search_f):
        self.c.execute(
            f"SELECT {field} FROM {self.table_name} WHERE {search_f} = ?", [search])
        list = self.c.fetchall()
        return map(first, list)

    def get_value(self, search, field):
        "returns the value of field for the row where search_field equals search"
        value_list = self.get_value_list(search, field)
        return value_list[0]

    def value_matches(self, search, field, match_value):
        "returns if the given search term for the field matches the given value"
        value = self.get_value(search, field)

        return match_value == value

    def value_exists(self, search, search_field):
        "returns true if a row where search_field equals search exists"
        return search in self.get_field(search_field)
        #value_list = self.get_value_list(search, "1")
        #return bool(value_list)

    def create(self, field_names):
        "creates a table with field_names"
        fields = map(add_type, field_names)
        field_string = list_to_string(fields)
        self.c.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} {field_string}")
        self.db.commit()

    def create_not_text(self,field_names):
        fields = []
        for f in field_names:
            if field_names[f] == "TEXT":
                fields.append(add_type(f))
            else:
                fields.append(add_other_types(f, field_names[f]))
        field_string = list_to_string(fields)
        self.c.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} {field_string}")
        self.db.commit()

    def get_non_main_value(self, search_type, search_query, value):
        ""
        self.c.execute(
            f"SELECT {value} FROM {self.table_name} WHERE {search_type} = '{search_query}'")
        return self.c.fetchone()

    def get_all_values(self):
        self.c.execute(f"SELECT * FROM {self.table_name}")
        return self.c.fetchall()

    def get_main_value_from_conditions(self,parameters,conditions):
        if not len(parameters) == len(conditions):
            return "error"

        conditional_string = "WHERE "
        for row in range(len(parameters)):
            parameter = parameters[row]
            condition = conditions[row]
            equal_statement = f"{parameter} = '{condition}'"

            if not row == 0:
                equal_statement = " AND " + equal_statement
            
            conditional_string += equal_statement

        #{search_type} = '{search_query}'
        self.c.execute(
            f"SELECT {self.search_field} FROM {self.table_name} {conditional_string}")
        #print(conditional_string)
        return self.c.fetchone()

    # def edit_main_value_from_conditions(self, parameters, conditions,new_value):
    #     if not len(parameters) == len(conditions):
    #         return "error"

    #     conditional_string = "WHERE "
    #     for row in range(len(parameters)):
    #         parameter = parameters[row]
    #         condition = conditions[row]
    #         equal_statement = f"{parameter} = '{condition}'"

    #         if not row == 0:
    #             equal_statement = " AND " + equal_statement

    #         conditional_string += equal_statement

    #     #{search_type} = '{search_query}'
    #     # print(
    #     #     f"UPDATE {self.table_name} SET {self.search_field} = {new_value} {conditional_string}")

    #     self.c.execute(
    #         f'''UPDATE {self.table_name} SET {self.search_field} = '{new_value}' {conditional_string}''')

    def update_value(self, field, new, search_query):
        self.c.execute(f"UPDATE {self.table_name} SET {field} = {new} WHERE {self.search_field} = '{search_query}'")
        self.db.commit()

    def delete_value_from_conditions(self,parameters,conditions):
        if not len(parameters) == len(conditions):
            return "error"

        conditional_string = "WHERE "
        for row in range(len(parameters)):
            parameter = parameters[row]
            condition = conditions[row]
            equal_statement = f"{parameter} = '{condition}'"

            if not row == 0:
                equal_statement = " AND " + equal_statement

            conditional_string += equal_statement

        #{search_type} = '{search_query}'
        self.c.execute(
            f"DELETE FROM {self.table_name} {conditional_string}")
        #print(conditional_string)
        return True