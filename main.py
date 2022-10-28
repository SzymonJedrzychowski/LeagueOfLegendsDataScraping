from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
import os


def getWebsites(browser):
    browser.get("https://gol.gg/tournament/list/")
    data = []
    i = 1
    browser.find_element(By.XPATH, '//*[@id="leagues_top"]').click()
    browser.find_element(By.XPATH, '//*[@id="btn_refresh"]').click()

    while True:
        item = browser.find_elements(
            By.XPATH, '//*[@id="result_tab"]/table/tbody/tr[{}]/td[2]/a'.format(i))
        if item:
            data.append(item[0].get_attribute('href'))
            i += 1
        else:
            return data


def getGames(browser, tournamentLink):
    browser.get(tournamentLink.replace("stats", "matchlist"))

    try:
        data = []
        i = 1

        while True:
            item = browser.find_elements(
                By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr[{}]/td[1]/a'.format(i))
            if item:
                link = item[0].get_attribute('href')
                if link[-8:] == "preview/":
                    pass
                else:
                    data.append(link)
                i += 1
            else:
                return data
    except Exception as ex:
        print(ex)
        return data


def getGameData(browser, gameLink):
    browser.get(gameLink)
    data = {"team1": [], "team2": [], "result": 2}
    if gameLink[-8:] == "summary/":
        gameCount = len(browser.find_elements(By.CLASS_NAME, "pb-1"))
        gamesData = []
        for i in range(gameCount):
            link = browser.find_element(
                By.XPATH, '//*[@id="gameMenuToggler"]/ul/li[{}]/a'.format(2+i)).get_attribute("href")
            gamesData += getGameData(browser, link)
        return gamesData
    else:
        for i in range(1, 6):
            item = browser.find_element(
                By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/div/div/div[2]/div/div/div/div[1]/table/tbody/tr[{}]/td[1]/a[1]/img'.format(i))
            data["team1"].append(item.get_attribute("alt"))
        for i in range(1, 6):
            item = browser.find_element(
                By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/div/div/div[2]/div/div/div/div[2]/table/tbody/tr[{}]/td[1]/a[1]/img'.format(i))
            data["team2"].append(item.get_attribute("alt"))
        if browser.find_element(By.XPATH, "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div").text[-3:] == "WIN":
            data["result"] = 1
        return [data]


def main(browser):
    if os.path.isfile("data.json"):
        with open("data.json") as f:
            data = json.load(f)
        gameLinks = data["gameLinks"]
    else:
        gameLinks = []
        websiteLinks = getWebsites(browser)
        for i in websiteLinks:
            gameLinks += getGames(browser, i)

    gameData = []
    for j, i in enumerate(gameLinks):
        print(j)
        gameData += getGameData(browser, i)
        if (j+1)%100 == 0:
            data["gameData"] = gameData
            data["gameLinks"] = gameLinks
            with open("data.json", "w") as f:
                json.dump(data, f)
    data["gameData"] = gameData
    data["gameLinks"] = gameLinks
    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    browser = webdriver.Chrome(ChromeDriverManager().install())
    try:
        main(browser)
        browser.quit()
    except Exception as ex:
        print(ex)
        browser.quit()
