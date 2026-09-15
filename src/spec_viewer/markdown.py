"""GOV.UK formatting for viewer Markdown, preserved from the original renderer."""
import re
from bs4 import BeautifulSoup
from markdown import markdown
from markupsafe import Markup
from slugify import slugify

def render_govuk_markdown(text, make_safe=True, capitalise=False):
    """Render markdown as HTML with GOV.UK Design System classes."""
    if text is None:
        return ""

    soup = BeautifulSoup(markdown(text, extensions=["tables"]), "html.parser")
    add_govuk_markdown_attrs(soup)

    if capitalise:
        capitalise_first_visible_character(soup)

    if make_safe:
        return Markup(str(soup))
    return soup

def capitalise_first_visible_character(soup):
    """Capitalise the first letter in rendered content, ignoring HTML markup."""
    for node in soup.find_all(string=True):
        match = re.search(r"[A-Za-z]", str(node))
        if not match:
            continue
        position = match.start()
        text = str(node)
        node.replace_with(text[:position] + text[position].upper() + text[position + 1 :])
        return

def add_govuk_markdown_attrs(soup):
    """Add GOV.UK Design System classes to rendered markdown HTML."""
    for tag in soup.select("p"):
        tag["class"] = "govuk-body"

    for tag in soup.select("h1, h2, h3, h4, h5"):
        tag["id"] = slugify(tag.get_text())

    for tag in soup.select("h1"):
        tag["class"] = "govuk-heading-xl"

    for tag in soup.select("h2"):
        tag["class"] = "govuk-heading-l"

    for tag in soup.select("h3"):
        tag["class"] = "govuk-heading-m"

    for tag in soup.select("h4, h5"):
        tag["class"] = "govuk-heading-s"

    for tag in soup.select("ul"):
        tag["class"] = "govuk-list govuk-list--bullet"

    for tag in soup.select("ol"):
        tag["class"] = "govuk-list govuk-list--number"

    for tag in soup.select("table"):
        tag["class"] = "govuk-table"

    for tag in soup.select("thead"):
        tag["class"] = "govuk-table__head"

    for tag in soup.select("tbody"):
        tag["class"] = "govuk-table__body"

    for tag in soup.select("tr"):
        tag["class"] = "govuk-table__row"

    for tag in soup.select("th"):
        tag["class"] = "govuk-table__header"
        tag["scope"] = "col"

    for tag in soup.select("td"):
        tag["class"] = "govuk-table__cell"

    for tag in soup.select("a"):
        tag["class"] = "govuk-link"

    for tag in soup.select("hr"):
        tag["class"] = "govuk-section-break govuk-section-break--l"

    for tag in soup.select("code"):
        tag["class"] = "app-code"
