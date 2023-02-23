import csv

# open the original CSV file and read the data
with open('data/vedh-data.csv', 'r') as f:
    reader = csv.reader(f)
    # skip the header row
    next(reader)
    # iterate over each row in the file
    for row in reader:
        # get the time and count values from the row
        time = row[1]
        count = int(row[2])
        # determine the location
        location = row[0]
        # open the target CSV file for updating
        with open('data/thurs-m.csv', 'r+', newline='') as target_file:
            # read the existing data from the target CSV file
            target_reader = csv.DictReader(target_file)
            rows = [row for row in target_reader]
            # find the row with the matching time
            matching_row = next(
                (row for row in rows if row['time'] == time), None)
            # update the count value for the appropriate location
            if location == 'H':
                matching_row['howth_count'] = str(count)
            elif location == 'S':
                matching_row['sutton_count'] = str(count)
            # write the updated data back to the target CSV file
            target_file.seek(0)
            target_writer = csv.DictWriter(target_file, fieldnames=[
                                           'time', 'howth_count', 'sutton_count'])
            target_writer.writeheader()
            target_writer.writerows(rows)
