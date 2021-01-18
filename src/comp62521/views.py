from comp62521 import app
from comp62521.database import database
from flask import render_template, request


def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([(fmt % i).rstrip('0').rstrip('.') for i in item]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result


@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "averages", 'title': "Averaged Data"}
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE]
    tables.append({
        "id": 1,
        "title": "Average Authors per Publication",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_authors_per_publication(i)[1])
            for i in averages]})
    tables.append({
        "id": 2,
        "title": "Average Publications per Author",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_publications_per_author(i)[1])
            for i in averages]})
    tables.append({
        "id": 3,
        "title": "Average Publications in a Year",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_publications_in_a_year(i)[1])
            for i in averages]})
    tables.append({
        "id": 4,
        "title": "Average Authors in a Year",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_authors_in_a_year(i)[1])
            for i in averages]})

    args['tables'] = tables
    return render_template("averages.html", args=args)


@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset": dataset, "id": "coauthors", "title": "Co-Authors"}

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)


@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset": dataset}
    return render_template('statistics.html', args=args)


@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": status}

    if status == "publication_summary":
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()

    if status == "publication_author":
        args["title"] = "Publications by Author"
        args["data"] = db.get_publications_by_author()
        args["status"] = status
        return render_template('publications_by_author.html', args=args)

    if status == "publication_year":
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()

    if status == "author_year":
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()

    return render_template('statistics_details.html', args=args)

@app.route("/search_author")
def showSearch_Author():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"search_author"}
    args["title"] = "Search Authors"
    allAuthors = db.get_all_author_names_lower()

    if "authorName" in request.args:
        authorName = request.args.get("authorName")
        args["authorName"] = authorName
        matchedNum, matched = db.get_partial_match(authorName.lower(), allAuthors)


        if authorName.lower() in allAuthors:
            args["data"] = db.get_author_stat(authorName.lower())
            args["search"] = True
            args["invalid"] = False
        elif matchedNum == 1:
            args["data"] = db.get_author_stat(matched[0])
            args["search"] = True
            args["invalid"] = False
            args["authorName"] = matched[0]
        elif matchedNum > 1:
            args["search"] = False
            args["invalid"] = False
            args["multipleMatch"] = True
            args["matches"] = db.get_partial_match(authorName.lower(), allAuthors)
            args["sortedname"]=db.sort_result(authorName,args['matches'][1])

        else:
            args["invalid"] = True
    else:
        args["search"] = False
    
    return render_template('search_author.html', args=args)



@app.route("/author_stats")
def showAuthor_Stats():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"author_stat"}
    args["title"] = "Author Stats"
    if "authorName" in request.args:
        authorName = request.args.get("authorName")
        args["authorName"] = authorName
        args["data"] = db.get_author_stat(authorName.lower())
            
    return render_template('author_stats.html', args=args)


@app.route("/authorfirstlastsole")
def showAuthorsfirstlastsole():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"authors_count"}
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["title"] = "First/Last/Sole Author"
    args["data"] = db.get_author_details(start_year, end_year, pub_type)
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]

    return render_template('author_firstlastsole.html', args=args)


@app.route("/authorstatsbyclick")
def showAuthorSearchByClick():
    dataset=app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"author_stats_by_click"}
    args["title"] = "Author Stats"
    author = str(request.args.get("author"))
    author_found, NoPublications, NoFirstAuthor, NoLastAuthor, NoSoleAuthor, NoCoAuthor, AuthorType, ExCoAuthorsList , NoExCoAuthors , author_name = db.get_author_stats_by_click(author)
    args["authorfound"]=author_found
    args["author"]=author
    args["NoPublications"] = NoPublications
    args["NoFirstAuthor"] = NoFirstAuthor
    args["NoLastAuthor"] = NoLastAuthor
    args["NoSoleAuthor"] = NoSoleAuthor
    args["NoCoAuthor"] = NoCoAuthor
    args["authorname"] = author_name
    args["AuthorType"] = AuthorType
    args["ExCoAuthorsList"] = ExCoAuthorsList
    args["NoExCoAuthors"] = NoExCoAuthors

    return render_template("author_stats_by_click.html", args=args)
