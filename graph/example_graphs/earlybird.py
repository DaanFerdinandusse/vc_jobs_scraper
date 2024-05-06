# Standard
import logging

# Data structures to build the graph
from graph.node import Node
from graph.scraper_graph import ScraperGraph

# functions to be executed by the nodes
from graph.node_functions.flow_control import pass_through, add_result_object_to_context
from graph.node_functions.navigation import navigate_to_url

# Playwright
from playwright.sync_api import sync_playwright, Browser, Page


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)
        page: Page = browser.new_page()

        # Create a graph
        graph = ScraperGraph(page_driver=page)

        start_node = Node(id="1", function=pass_through, static_inputs={})
        navigate_to_page_node = Node(id="2", function=navigate_to_url, static_inputs={"url": "https://earlybird.com/portfolio"})


        graph.add_node(start_node)
        graph.add_node(navigate_to_page_node)
        graph.add_edge(start_node, navigate_to_page_node)


        graph.execute()
