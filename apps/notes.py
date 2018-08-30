import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

title = "Notes"

urls = dict(
  census_url="https://factfinder.census.gov/faces/affhelp/jsf/pages/" \
    + "metadata.xhtml?lang=en&type=table&id=table.en.ACS_16_1YR_B03002",
  karenx_url="http://www.karenx.com/blog/minorities-on-the-bachelor-when-do-" \
    + "they-get-eliminated/",
  five38_url="https://github.com/fivethirtyeight/data/tree/master/bachelorette",
  ba_wiki_url="https://en.wikipedia.org/wiki/The_Bachelor_(U.S._TV_series)",
  be_wiki_url="https://en.wikipedia.org/wiki/The_Bachelorette"
)

# TODO: Can this look cooler?
main_content = dcc.Markdown(
  """
  ## Data Sources
  
  #### Contestants
  * [538]({five38_url}) data
  * Supplemental data for Season 22 of the Bachelor and Season 14 of the 
    Bachelorette from Wikipedia
  
  #### Race
  * [karenx]({karenx_url})'s dataset
  * [US Census]({census_url}) 'Hispanic or Latino Origin by Race' 
    ACS 1-year variable
  * Individual sources listed for person-level race data

  #### Seasons
  * [Bachelor]({ba_wiki_url}) and [Bachelorette]({be_wiki_url}) Wikipedia pages
  """.format(**urls)
)

layout = utils.BSContainer(
  title=title,
  main_content=main_content)
