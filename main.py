from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
import os


def getWebsites(browser: object) -> list:
    """Get links to tournament pages

    :param browser: selenium webdriver
    :return: list of tournament links
    """
    # Open main page
    browser.get("https://gol.gg/tournament/list/")
    data = []
    i = 1

    # Sort tournaments (include only top leagues)
    browser.find_element(By.XPATH, '//*[@id="leagues_top"]').click()
    browser.find_element(By.XPATH, '//*[@id="btn_refresh"]').click()

    while True:
        # Get tournament element
        item = browser.find_elements(
            By.XPATH, '//*[@id="result_tab"]/table/tbody/tr[{}]/td[2]/a'.format(i))
        if item:
            # Get the link of the tournament
            data.append(item[0].get_attribute('href'))
            i += 1
        else:
            return data


def getGames(browser: object, tournamentLink: str) -> list:
    """Get links to games and series

    :param browser: selenium webdriver
    :param tournamentLink: link to specific tournament
    :return: list of games and series links
    """
    # Open the tournament page
    browser.get(tournamentLink.replace("stats", "matchlist"))

    data = []
    i = 1

    while True:
        # Get the game element
        item = browser.find_elements(
            By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr[{}]/td[1]/a'.format(i))
        if item:
            # Get the link of the element
            link = item[0].get_attribute('href')
            if link[-8:] == "preview/":
                pass
            else:
                data.append(link)
            i += 1
        else:
            return data


def getGameData(browser: object, gameLink: str):
    """Get data of games and series

    :param browser: selenium webdriver
    :param gameLink: link to specific game or series
    :return: list that includes dict of game or series data
    """
    # Open the game page
    browser.get(gameLink)
    data = {"team1": [], "team2": [], "result": 2}

    # "summary/" is only in series links
    if gameLink[-8:] == "summary/":
        # Get number of games
        gameCount = len(browser.find_elements(By.CLASS_NAME, "pb-1"))
        gamesData = []
        for i in range(gameCount):
            # Get link to specific game
            link = browser.find_element(
                By.XPATH, '//*[@id="gameMenuToggler"]/ul/li[{}]/a'.format(2+i)).get_attribute("href")

            # Get data of game calling the getGameData function with game link
            gamesData += getGameData(browser, link)

        return gamesData
    else:
        for i in range(1, 6):
            # Get element of champion icon
            item = browser.find_element(
                By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/div/div/div[2]/div/div/div/div[1]/table/tbody/tr[{}]/td[1]/a[1]/img'.format(i))

            # Get name of champion
            data["team1"].append(item.get_attribute("alt"))

        for i in range(1, 6):
            # Get element of champion icon
            item = browser.find_element(
                By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/div/div/div[2]/div/div/div/div[2]/table/tbody/tr[{}]/td[1]/a[1]/img'.format(i))

            # Get name of champion
            data["team2"].append(item.get_attribute("alt"))

        # Get result of the game (change the data in dict to 1 if team 1 won)
        if browser.find_element(By.XPATH, "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div").text[-3:] == "WIN":
            data["result"] = 1

        return [data]


def main(browser):
    """
    :param browser: selenium webdriver
    """
    gameLinks = []
    # Get the links of games if file is present
    if os.path.isfile("data.json"):
        with open("data.json") as f:
            data = json.load(f)
        gameLinks = data.get("gameLinks", [])

    if not gameLinks:
        data = {}
        # Get tournament links
        tournamentLinks = getWebsites(browser)
        for i in tournamentLinks:
            gameLinks += getGames(browser, i)

    gameData = []
    for j, i in enumerate(gameLinks):
        print("{}/{}".format(j, len(gameLinks)))
        gameData += getGameData(browser, i)

        # Save every 100 links
        if (j+1) % 100 == 0:
            if not "gameLinks" in data:
                data["gameLinks"] = gameLinks
            data["gameData"] = gameData
            with open("data.json", "w") as f:
                json.dump(data, f)

    # Save at the end
    data["gameData"] = gameData
    data["gameLinks"] = gameLinks
    with open("data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    # Install browser and create webdriver object
    browser = webdriver.Chrome(ChromeDriverManager().install())
    try:
        main(browser)
        browser.quit()
    except Exception as ex:
        print(ex)
        browser.quit()
