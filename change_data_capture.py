import csv
import datetime


def to_date_object(date_string): return datetime.datetime.strptime(
    date_string, '%d.%m.%Y')


def order_date(x): return x[1]


def parse_csv_into_rows(file_path):
    with open(file_path, 'r') as file:
        txt = file.read()
        rows_raw = txt.split('\n')
        rows_cleansed = [row.split(',') for row in rows_raw[1:-1]]
        return rows_cleansed


def extract_inserts(cleansed_rows):
    insert_rows = [row[0:-1] for row in cleansed_rows if row[3] == 'I']
    return insert_rows


def extract_updates(cleansed_rows):
    update_rows = [row[0:-1] for row in cleansed_rows if row[3] == 'U']
    return update_rows


def get_most_recent_updates(update_rows):
    ids = get_ids(update_rows)
    idsGrouped = {}
    for row in cleansed_rows:
        # check if the first element is in the dictionary
        if row[0] in idsGrouped:
            # if yes, append the second element to the list
            idsGrouped[row[0]].append((row))
        else:
            # if not, create a new list with the second element
            idsGrouped[row[0]] = [(row)]

    for id in idsGrouped:
        dts = []
        for row in idsGrouped[id]:
            date_dt = to_date_object(row[1])
            row[1] = date_dt

        idsGrouped[id] = sorted(
            idsGrouped[id], key=order_date, reverse=True)[0]

    return idsGrouped


def extract_deletes(cleansed_rows):
    delete_rows = [row[0:-1] for row in cleansed_rows if row[3] == 'D']
    return delete_rows


def append_insert_to_current_customers(file_path, insert_rows):
    with open(file_path, 'a') as file:
        writer = csv.writer(file)
        [writer.writerow(row) for row in insert_rows]


def get_ids(rows):
    ids = [row[0] for row in rows]
    return ids


def delete_row_from_customers_current(file_path, delete_rows_list):
    # open the csv file in read mode
    with open(file_path, 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)

    # open the csv file in write mode
    with open(file_path, 'w') as writeFile:
        writer = csv.writer(writeFile)
        for line in lines:
            id = line[0]
            # check the condition and write to the file accordingly
            ids = get_ids(delete_rows_list)
            if id in ids:
                continue
            else:
                writer.writerow(line)


def transform_date_to_str(row):
    row[1] = row[1].strftime('%d.%m.%Y')
    return row


def update_row_from_customers_current(file_path, update_rows_dict):
    # open the csv file in read mode
    with open(file_path, 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)

    # open the csv file in write mode
    with open(file_path, 'w') as writeFile:
        writer = csv.writer(writeFile)
        for index, line in enumerate(lines):
            if index == 0:
                writer.writerow(['CUSTOMER_ID', 'UPDATE_DATE', 'LOCATION'])
                continue
            id = line[0]
            # check the condition and write to the file accordingly
            if id in update_rows_dict:

                row = transform_date_to_str(update_rows_dict[id])[0:-1]
                curent_str_date = line[1]
                current_dt_date = to_date_object(curent_str_date)
                update_row_str_date = update_rows_dict[id][1]
                update_row_dt_date = to_date_object(update_row_str_date)
                if update_row_dt_date > current_dt_date:
                    writer.writerow(row)
                else:
                    writer.writerow(line)
            else:
                writer.writerow(line)


if __name__ == '__main__':
    cleansed_rows = parse_csv_into_rows('data/customers_update.csv')
    rows_to_insert = extract_inserts(cleansed_rows)
    rows_to_delete = extract_deletes(cleansed_rows)

    update_rows = extract_updates(cleansed_rows)
    most_recent_updates_by_id = get_most_recent_updates(update_rows)

    append_insert_to_current_customers(
        'data/customers_current.csv', rows_to_insert)
    update_row_from_customers_current(
        'data/customers_current.csv', most_recent_updates_by_id)
    delete_row_from_customers_current(
        'data/customers_current.csv', rows_to_delete)
