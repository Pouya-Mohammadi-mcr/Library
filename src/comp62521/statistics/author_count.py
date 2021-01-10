def appearing_first(name, author_list):
    if name == author_list[0] and len(author_list) > 1:
        return 1
    return 0

def appearing_first_for_lists(name, list_of_author_list):
    occurrence = 0
    for a in list_of_author_list:
        occurrence += appearing_first(name, a)
    return occurrence

def appearing_last(name, author_list):
    if name == author_list[-1] and len(author_list) > 1:
        return 1
    return 0

def appearing_last_for_lists(name, list_of_author_list):
    occurrence = 0
    for a in list_of_author_list:
        occurrence += appearing_last(name, a)
    return occurrence

def appearing_sole(name,author_list):
    if len(author_list) == 1 and (name == author_list[0]):
        return 1
    return 0

def appearing_sole_for_lists(name, list_of_author_list):
    occurrence = 0
    for a in list_of_author_list:
        occurrence += appearing_sole(name, a)
    return occurrence