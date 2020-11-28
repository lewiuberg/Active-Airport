def unpack_list(lst):  # Oxford comma
    if not isinstance(lst, str):
        lst = [str(item) for item in lst]
    if len(lst) == 0:
        return
    if len(lst) == 1:
        return ", ".join(lst)
    if len(lst) == 2:
        return ", and ".join(lst)
    else:
        first_part = lst[:-1]
        last_part = lst[-1]
        return ", ".join(first_part) + ", and " + last_part


def word_search(df, *words):
    if not words or len(words[0]) < 1:
        return

    col_count: int = 0
    sum_words: int = 0
    found_words: str = []

    if isinstance(words[0], str):
        words = [word for word in words]
    else:
        words = list(*words)
        print(words)

    for word in words:
        col_count = 0
        sum_word = 0
        for column in df:
            if df[column].dtype == object or df[column].dtype == str:
                col_count += 1
                sum_word += df[column].str.contains(f"^{word}$").sum()
                if df[column].str.contains(f"^{word}$").any():
                    if word not in found_words:
                        found_words.append(word)
        sum_words += sum_word
    if len(found_words) == 0:
        found_words = words
    print("Columns of dtype str or object:", col_count)
    print(
        f"Instances of {unpack_list(found_words)} in the dataframe: {sum_words}"
    )


def find_missing_values(df):
    column_names = (df.columns[df.isnull().any() == True]).format()
    miss_columns = df.isna().any().sum()
    miss_values = df.isna().sum().sum()
    print(f"Instances of missing data: {miss_values}")
    print(f"Columns with missing data: {miss_columns}")
    print(f"Column names with missing data: {unpack_list(column_names)}")


def path_checker(path):
    from pathlib import Path
    path = Path(path)

    if path.exists():
        if path.is_dir():
            print(f"'{path}' is directory")
        else:
            if path.is_file():
                print(f"'{path}' is a file")
        return True

    else:
        print(f"'{path}' does not exist.")
        return False


def df_location_data(df, search_col):
    import pandas as pd
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    geolocator = Nominatim(user_agent="my_geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=.1)
    # Find the location.
    df['location'] = df[search_col].apply(geocode)
    # Extract point to its own columns.
    df['point'] = df['location'].apply(lambda loc: tuple(loc.point)
                                       if loc else None)
    # split point column into latitude, longitude and altitude columns.
    df[['latitude', 'longitude',
        'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)

    return df


def missing_location(df):
    col_criteria = df.isnull().any(axis=0)
    miss_col = df[col_criteria.index[col_criteria]]

    miss_only = miss_col[miss_col.isnull().any(axis=1)]

    row_criteria = df.isnull().any(axis=1)
    miss_row = df[row_criteria]

    return miss_col, miss_row, miss_only


def replace_df_ax_name(df, find, replace_with="", axis=0):
    import pandas as pd
    dff = df.copy()

    if axis == 1:  # <-- Columns
        dff = dff.T

    dff_row = dff.index.to_list()
    dff_dict = {i: dff_row[i] for i in range(len(dff_row))}

    change_index: list = []
    change_dict: dict = {}

    for i, v in dff_dict.items():
        if find in v:
            change_index.append(i)
            if replace_with == "d_to_datetime":
                v = pd.to_datetime(v)
            else:
                v = v.replace(find, replace_with)
            change_dict[i] = v

    dff_dict.update(change_dict)
    dff.index = list(dff_dict.values())

    if axis == 1:  # <-- Columns
        dff = dff.T

    return dff
