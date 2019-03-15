import datetime
import logging
import os
import random
import uuid

intro_msg = "Welcome to Baseball! (WIP)"

class gamestate:
    status = None
    mode = "simulation"
    gameid = None
    actionNum = 0
    score_away = 0
    score_home = 0
    inning = 1
    inning_half = "top"
    outs = 0
    strikes = 0
    defense_1b = None
    defense_2b = None
    defense_3b = None
    defense_hp = None
    defense_field = None
    defense_dd = None
    offense_1b = None
    offense_2b = None
    offense_3b = None
    offense_ab = None
    lineup_away = []
    lineup_home = []
    lineupPos_away = 1
    lineupPos_home = 1
    lineupMax_away = 0
    linupMax_home = 0

def adv_inning(gs):
    if gs.inning_half == "top":
        if gs.inning == 9:
            if gs.score_home > gs.score_away:
                gs.status = "ended"
        gs.inning_half = "bottom"
        gs.defense_1b = gs.lineup_away[1]
        gs.defense_2b = gs.lineup_away[2]
        gs.defense_3b = gs.lineup_away[3]
        gs.defense_hp = gs.lineup_away[4]
        gs.defense_field = gs.lineup_away[5]
        gs.defense_dd = gs.lineup_away[6]
    else:
        if gs.inning < 9 or gs.score_away == gs.score_home:
            gs.inning_half = "top"
            gs.inning += 1
        else:
            gs.status = "ended"
        gs.defense_1b = gs.lineup_home[1]
        gs.defense_2b = gs.lineup_home[2]
        gs.defense_3b = gs.lineup_home[3]
        gs.defense_hp = gs.lineup_home[4]
        gs.defense_field = gs.lineup_home[5]
        gs.defense_dd = gs.lineup_home[6]
    gs.offense_1b = None
    gs.offense_2b = None
    gs.offense_3b = None
    return gs

def adv_out(gs, mode):
    if mode == "batter":
        gs.strikes = 0
        gs = adv_batter(gs)

    if gs.outs < 2:
        gs.outs += 1
    else:
        gs.outs = 0
        gs = adv_inning(gs)
    return gs

def adv_strike(gs):
    if gs.strikes < 2:
        gs.strikes += 1
    else:
        gs = adv_out(gs, "batter")
    return gs

def adv_hit(gs, hit_type):
    print("it's a {}! We are {}.".format(hit_type, gs.status))
    gs.strikes = 0
    if hit_type == "single" or hit_type == "bunt_single" or hit_type == "sacrifice":
        if gs.offense_3b:
            gs.offense_3b = None
            gs = score_run(gs)
        if gs.offense_2b:
            gs.offense_3b = gs.offense_2b
            gs.offense_2b = None
        if gs.offense_1b:
            gs.offense_2b = gs.offense_1b
            gs.offense_1b = None
        if hit_type == "sacrifice":
            gs = adv_out(gs, "batter")
        else:
            gs.offense_1b = gs.offense_ab
    elif hit_type == "long_single":
        if gs.offense_3b:
            gs.offense_3b = None
            gs = score_run(gs)
        if gs.offense_2b:
            gs.offense_2b = None
            gs = score_run(gs)
        if gs.offense_1b:
            gs.offense_2b = gs.offense_1b
        gs.offense_1b = gs.offense_ab
    elif hit_type == "double":
        if gs.offense_3b:
            gs.offense_3b = None
            gs = score_run(gs)
        if gs.offense_2b:
            gs.offense_2b = None
            gs = score_run(gs)
        if gs.offense_1b:
            gs.offense_3b = gs.offense_1b
            gs.offense_1b = None
        gs.offense_2b = gs.offense_ab
    elif hit_type == "triple":
        if gs.offense_3b:
            gs.offense_3b = None
            gs = score_run(gs)
        if gs.offense_2b:
            gs.offense_2b = None
            gs = score_run(gs)
        if gs.offense_1b:
            gs.offense_1b = None
            gs = score_run(gs)
        gs.offense_3b = gs.offense_ab
    elif hit_type == "homerun":
        if gs.offense_3b:
            gs.offense_3b = None
            gs = score_run(gs)
        if gs.offense_2b:
            gs.offense_2b = None
            gs = score_run(gs)
        if gs.offense_1b:
            gs.offense_1b = None
            gs = score_run(gs)
        gs = score_run(gs)
    gs = adv_batter(gs)
    return gs

def adv_batter(gs):
    if gs.inning_half == "top":
        if gs.lineupPos_away < (gs.lineupMax_away - 1):
            gs.lineupPos_away += 1
        else:
            gs.lineupPos_away = 1
    else:
        if gs.lineupPos_home < (gs.lineupMax_home - 1):
            gs.lineupPos_home += 1
        else:
            gs.lineupPos_home = 1
    return gs

def adv_steal(gs, sbDef):
    print("The runner goes... and he's {}!".format(sbDef))
    if gs.offense_3b:
        gs.offense_3b = None
        if sbDef == "out":
            gs = adv_out(gs, "runner")
        else:
            gs = score_run(gs)
    elif gs.offense_2b:
        if sbDef == "out":
            gs = adv_out(gs, "runner")
            gs.offense_2b = None
        else:
            gs.offense_3b = gs.offense_2b
            gs.offense_2b = None
    elif gs.offense_1b:
        if sbDef == "out":
            gs = adv_out(gs, "runner")
            gs.offense_1b = None
        else:
            gs.offense_2b = gs.offense_1b
            gs.offense_1b = None
    return(gs)

def score_run(gs):
    if gs.inning_half == "top":
        gs.score_away += 1
    else:
        gs.score_home += 1
    print("He Scores!")
    return gs

def write_gamelog(gs, action, logFile, mode):
    if action == "start":
        if mode=="log":
            logLine="{} gameid={} lineup_away={} lineup_home={} actionNum={} action={}\n".format(datetime.datetime.now(), gs.gameid, gs.lineup_away, gs.lineup_home, gs.actionNum, action)
            logFile.write(logLine)
        else:
            teamlistPath = open("games/{}.{}".format(gs.gameid + "_teamlist", mode), "w+")
            fieldLine="gameid,team,lineupPos,name,home\n"
            teamlistPath.write(fieldLine)
            for x in range(1,gs.lineupMax_away):
                logLine="{},{},{},{},false\r\n".format(gs.gameid,gs.lineup_away[0],x,gs.lineup_away[x])
                teamlistPath.write(logLine)
            for y in range(1,gs.lineupMax_home):
                logLine="{},{},{},{},true\r\n".format(gs.gameid,gs.lineup_home[0],y,gs.lineup_home[y])
                teamlistPath.write(logLine)
            gameFields="gameid,actionTime,actionNum,action,score_away,score_home,inning_half,inning,outs,strikes,defense_1b,defense_2b,defense_3b,defense_hp,defense_field,defense_dd,offense_ab,offense_1b,offense_2b,offense_3b,lineupPos_away,lineupPos_home\r\n"
            logFile.write(gameFields)
    elif action == "end":
        if mode=="log":
            logLine="{} gameid={} actionNum={} action={}\r\n".format(datetime.datetime.now(), gs.gameid, gs.actionNum, action)
            logFile.write(logLine)
    else:
        if mode=="log":
            logLine = "{} gameid={} actionNum={} action={} score_away={} score_home={} inning_half={} inning={} outs={} strikes={} defense_1b=\"{}\" defense_2b=\"{}\" defense_3b=\"{}\" defense_hp=\"{}\" defense_field=\"{}\" defense_dd=\"{}\" offense_ab=\"{}\" offense_1b=\"{}\" offense_2b=\"{}\" offense_3b=\"{}\" lineupPos_away={} lineupPos_home={}\r\n".format(datetime.datetime.now(), gs.gameid, gs.actionNum, action, gs.score_away, gs.score_home, gs.inning_half, gs.inning, gs.outs, gs.strikes, gs.defense_1b, gs.defense_2b, gs.defense_3b, gs.defense_hp, gs.defense_field, gs.defense_dd, gs.offense_ab, gs.offense_1b, gs.offense_2b, gs.offense_3b, gs.lineupPos_away, gs.lineupPos_home)
        else:
            logLine = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\r\n".format(gs.gameid, datetime.datetime.now(), gs.actionNum, action, gs.score_away, gs.score_home, gs.inning_half, gs.inning, gs.outs, gs.strikes, gs.defense_1b, gs.defense_2b, gs.defense_3b, gs.defense_hp, gs.defense_field, gs.defense_dd, gs.offense_ab, gs.offense_1b, gs.offense_2b, gs.offense_3b, gs.lineupPos_away, gs.lineupPos_home)
        logFile.write(logLine)

    
    gs.actionNum += 1
    return(gs)

print(intro_msg)
gamesDir = "games"
if not os.path.exists(gamesDir):
    os.mkdir(gamesDir)
    print("Directory " , gamesDir ,  " Created ")
else:    
    print("Directory " , gamesDir ,  " already exists")

logMode = "csv"
gs_current = gamestate()
gs_current.status = "setup"

gs_current.lineup_away = ["The Pituitary Giants","Adrienne Barbeaubot","Parts Hilton","Francis Clampazzo","Bender Rodriguez","Tinny Tim","Malfunctioning Eddie"]
gs_current.lineup_home = ["The Anaheim Angels of Purgatory","Carmine Durango","Tequila Rizzo","Happy Braggadacio","Nicky Jackhammer","Danny Falcone","Bradley Kane"]
gs_current.lineupMax_away = len(gs_current.lineup_away)
gs_current.lineupMax_home = len(gs_current.lineup_home)

gs_current.defense_1b = gs_current.lineup_home[1]
gs_current.defense_2b = gs_current.lineup_home[2]
gs_current.defense_3b = gs_current.lineup_home[3]
gs_current.defense_hp = gs_current.lineup_home[4]
gs_current.defense_field = gs_current.lineup_home[5]
gs_current.defense_dd = gs_current.lineup_home[6]

gs_current.gameid = 'G' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + hex(uuid.getnode())[-4:]
gamePath = open("games/{}.{}".format(gs_current.gameid, logMode), "w+")

gs_current.status = "in progress"
gs_current = write_gamelog(gs_current, "start", gamePath, logMode)
while gs_current.status == "in progress":
    if (gs_current.inning_half == "top"):
        gs_current.offense_ab = gs_current.lineup_away[gs_current.lineupPos_away]
    else:
        gs_current.offense_ab = gs_current.lineup_home[gs_current.lineupPos_home]
    game_summary = "{} of {}. {} outs. {} - {}. {} strikes. {} up to bat.".format(gs_current.inning_half,gs_current.inning,gs_current.outs,gs_current.score_away,gs_current.score_home,gs_current.strikes,gs_current.offense_ab)
    print(game_summary)
    
    if (gs_current.mode == "simulation"):
        if gs_current.offense_1b or gs_current.offense_2b or gs_current.offense_3b:
            steal_chance = random.randint(1,100)
        else:
            steal_chance =0
        if steal_chance > 85:
            success = random.randint(1,10)
            if success > 4:
                sbDef = "safe"
            else:
                sbDef = "out"
            action = "steal" + sbDef
            gs_current = write_gamelog(gs_current, action, gamePath, logMode)
            gs_current = adv_steal(gs_current, sbDef)
        else:
            chance = random.randint(1,100)
            if chance <= 50:
                if gs_current.strikes == 2:
                    #gs_current = write_gamelog(gs_current, "strike", gamePath, logMode)
                #else:
                    gs_current = write_gamelog(gs_current, "strikeout", gamePath, logMode)
                gs_current = adv_strike(gs_current)
            elif chance <= 75:
                hit_chance = random.randint(1,100)
                if (hit_chance <= 20 and (gs_current.offense_1b or gs_current.offense_2b or gs_current.offense_3b) and gs_current.outs < 2 and gs_current.strikes < 2) or (hit_chance <=5 and gs_current.strikes < 2):
                    safe_chance = random.randint(1,4)
                    if safe_chance < 4:
                        hit_type = "sacrifice"
                    else:
                        hit_type = "bunt_single"
                elif hit_chance <= 50:
                    long_chance = random.randint(1,3)
                    if long_chance == 3:
                        hit_type = "long_single"
                    else:
                        hit_type = "single"
                elif hit_chance <= 85:
                    hit_type = "double"
                elif hit_chance <= 91:
                    hit_type = "triple"
                else:
                    hit_type = "homerun"
                gs_current = write_gamelog(gs_current, hit_type, gamePath, logMode)
                gs_current = adv_hit(gs_current, hit_type)
            else:
                gs_current = write_gamelog(gs_current, "out", gamePath, logMode)
                gs_current = adv_out(gs_current, "batter")
    elif gs_current.mode == "input":
        batterCheck = True
        while batterCheck:
            action = input("What is happening? ")
            if action == "strike":
                if gs_current.strikes == 2:
                    #gs_current = write_gamelog(gs_current, "strike", gamePath, logMode)
                #else:
                    gs_current = write_gamelog(gs_current, "strikeout", gamePath, logMode)
                gs_current = adv_strike(gs_current)
                batterCheck = False
            elif action == "steal":
                stealCheck = True
                while stealCheck:
                    outcome = input("Safe or out? ")
                    if outcome == "safe" or outcome == "out":
                        logAction = action + outcome
                        gs_current = write_gamelog(gs_current, logAction, gamePath, logMode)
                        gs_current = adv_steal(gs_current, outcome)
                        stealCheck = False
                    else:
                        print("Not a valid input, try again")
            elif action == "out":
                gs_current = write_gamelog(gs_current, "out", gamePath, logMode)
                gs_current = adv_out(gs_current, "batter")
                batterCheck = False
            elif action in ["single", "double", "triple", "homerun", "long_single", "sacrifice", "bunt_single"]:
                gs_current = write_gamelog(gs_current, action, gamePath, logMode)
                gs_current = adv_hit(gs_current, action)
                batterCheck = False
                    
    if gs_current.inning > 8 and gs_current.inning_half == "bottom" and gs_current.score_home > gs_current.score_away:
        gs_current.status = "ended"
gs_current = write_gamelog(gs_current, "end", gamePath, logMode)

gamePath.close()
print("Final Score: {}, {}. {}, {}.".format(gs_current.lineup_away[0],gs_current.score_away,gs_current.lineup_home[0],gs_current.score_home,))
print("Game Over")