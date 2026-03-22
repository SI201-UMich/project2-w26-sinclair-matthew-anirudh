# SI 201 P2
# Your name: Matthew Huang
# Your student id: 17382251
# Your email: matthhua@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Matthew: I did not use GenAI on this assignment.
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    # Open the html file for reading.
    with open(html_path, encoding="utf-8-sig") as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

        # Get all link tags.
        tags = soup.find_all('div', class_="t1jojoys dir dir-ltr")
        results = []
        for listing in tags:

            # Add id and listing title to list.
            id = listing.get("id")
            separator_index = id.find("_")
            id = id[separator_index + 1:]
            results.append((listing.text, id))

    return results

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    # Get and open html file.
    file_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(file_path, "html_files", f"listing_{listing_id}.html")
    with open(file_path, encoding="utf-8-sig") as listing_file:
        inner_dict = {}
        soup = BeautifulSoup(listing_file, 'html.parser')

        # Get li tags with correct class, then filter for policy number.
        li_tags = soup.find_all("li", class_="f19phm7j dir dir-ltr")
        for li_tag in li_tags:
            temp = li_tag.text
            if li_tag.text.find("Policy number: ") >= 0:
                inner_span_tag_list = li_tag.find_all("span")
                policy = inner_span_tag_list[0].text
                if policy.lower() == "pending":
                    policy = "Pending"
                elif policy.lower() == "exempt":
                    policy = "Exempt"
                inner_dict["policy_number"] = policy

        # Find tags to determine host type.
        span_tags = soup.find_all("span", class_="_1mhorg9")
        found_superhost = False
        for span_tag in span_tags:
            if span_tag.text == "Superhost":
                inner_dict["host_type"] = span_tag.text
                found_superhost = True
        
        # Set as regular if the host type was not found.
        if not found_superhost:
            inner_dict["host_type"] = "regular"

        # Find host name(s).
        # hnwb2pb dir dir-ltr (class for actual host names)
        h2_tags = soup.find_all("h2", class_="hnwb2pb dir dir-ltr")
        for tag in h2_tags:

            # Extract name.
            expression = r"Hosted\sby\s(.+)\b"
            name = re.findall(expression, tag.text)
            if len(name) > 0:
                name = name[0]
                inner_dict["host_name"] = name

        # Determine room type.
        h2_tags = soup.find_all("h2", class_="_14i3z6h")
        for tag in h2_tags:
            tag_text = tag.text
            if tag_text.lower().find("hosted by") >= 0:

                # Also determine room type.
                if tag_text.lower().find("private") >= 0:
                    inner_dict["room_type"] = "Private Room"
                elif tag_text.lower().find("shared") >= 0:
                    inner_dict["room_type"] = "Shared Room"
                else:
                    inner_dict["room_type"] = "Entire Room"

        # Try again for room type if not found.
        if inner_dict.get("roomt_type", None) is None:
            h2_tags = soup.find_all("div", class_="_tqmy57")
            for tag in h2_tags:
                tag_text = tag.text
                if tag_text.lower().find("hosted by") >= 0:

                    # Also determine room type.
                    if tag_text.lower().find("private") >= 0:
                        inner_dict["room_type"] = "Private Room"
                    elif tag_text.lower().find("shared") >= 0:
                        inner_dict["room_type"] = "Shared Room"
                    else:
                        inner_dict["room_type"] = "Entire Room"

        # Find location rating.
        rating = 0.0
        span_tags = soup.find_all("span", class_="_12si43g")
        if len(span_tags) > 0:

            # Get number string out of the first span tag.
            expression = r"\d\.\d"
            rating = float(re.findall(expression, span_tags[0].text)[0])
            
        inner_dict["location_rating"] = rating

        

    return {listing_id: inner_dict}


    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    # Get listing results.
    database_list = []
    results_list = load_listing_results(html_path)

    # Create tuple for each result.
    for result in results_list:
        title = result[0]
        id = result[1]

        # Get inner dictionary from get_listing_details.
        details = get_listing_details(id)[id]

        # Create and append tuple.
        database_list.append((title, id, details["policy_number"], details["host_type"],
                             details["host_name"], details["room_type"], details["location_rating"]))
        
    return database_list

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # Check that the number of listings extracted is 18.
        # Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # Call get_listing_details() on each listing id above and save results in a list.
        listing_details_list = []
        for id in html_list:
            listing_details_list.append(get_listing_details(id))

        # Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(listing_details_list[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(listing_details_list[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(listing_details_list[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(listing_details_list[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        database_list = create_listing_database(self.search_results_path)
        for listing in database_list:
            self.assertEqual(len(listing), 7)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(database_list[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)