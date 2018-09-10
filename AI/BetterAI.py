  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


#Author: Brandon Delplanche
#Author: Chris Lytle
#
#Date: 9/10/18
#

class AIPlayer(Player):


    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Better AI")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None


    ##
    # getPlacement
    #
    # Better AI uses a different method of placing it's defenses.
    # It places it's buildings in the front of it's side so that it would be able to defend it's worker and
    # send troops to attack.
    # Places the enemy food in the opposite side of the enemy's side
    #
    ##
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(4, 3), (5, 1),
                    (0, 3), (1, 3), (2, 3), (3, 3),
                    (5, 3), (6, 3), (7, 3),
                    (8, 3), (9, 3)]
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []

            for i in range(0, numToPlace):
                move = None
                a = 0
                b = 6
                while move is None:
                    # Choose any x location
                    x = a
                    # Choose any y location on enemy side of the board
                    y = b
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr = True
                    else:
                        if a == 9:
                            a = 0
                            b = b + 1
                        else:
                            a = a + 1
                moves.append(move)
            return moves
        else:
            return None  # should never happen


    #
    # getMove
    # Method used to decide the moves of the AI.
    # If there is no workers, build one.
    # Move worker towards food and back
    # Have drone attack enemy tunnel.
    # Every time there is enough food, build drone.
    #
    ##
    def getMove(self, currentState):
        # Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        # the first time this method is called, the food and tunnel locations
        # need to be recorded in their respective instance variables
        if self.myTunnel is None:
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if self.myFood is None:
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            # find the food closest to the tunnel
            bestDistSoFar = 1000  # i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if dist < bestDistSoFar:
                    self.myFood = food
                    bestDistSoFar = dist

        # if I don't have a worker, give up
        numAnts = len(myInv.ants)
        if numAnts == 1:
            if myInv.foodCount <= 0:
                return Move(END, None, None)

        # if the worker has already moved, we're done
        workerList = getAntList(currentState, me, (WORKER,))
        if len(workerList) < 1:
            if myInv.foodCount >= 1:
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)
        else:
            myWorker = workerList[0]
            if myWorker.hasMoved:
                return Move(END, None, None)

        # if the queen is on the anthill move her
        myQueen = myInv.getQueen()
        if myQueen.coords == myInv.getAnthill().coords:
            return Move(MOVE_ANT, [myInv.getQueen().coords, (5, 3)], None)

        # if the hasn't moved, have her move in place so she will attack
        if not myQueen.hasMoved:
            return Move(MOVE_ANT, [myQueen.coords], None)

        # if I have the food and the anthill is unoccupied then
        # make a drone
        if myInv.foodCount >= 2:
            if getAntAt(currentState, myInv.getAnthill().coords) is None:
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        # Move all my drones towards the enemy
        myDrones = getAntList(currentState, me, (DRONE,))
        for drone in myDrones:
            if not drone.hasMoved:

                # Get enemy tunnel location
                tunnels = getConstrList(currentState, None, (TUNNEL,))
                if tunnels[0].coords[1] > 3:
                    enemyTunnel = tunnels[0]
                else:
                    enemyTunnel = tunnels[1]

                path = createPathToward(currentState, drone.coords,
                                        enemyTunnel.coords, UNIT_STATS[DRONE][MOVEMENT])
                return Move(MOVE_ANT, path, None)

        for worker in workerList:
            # if the worker has food, move toward tunnel
            if worker.carrying:
                path = createPathToward(currentState, worker.coords,
                                        self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)

            # if the worker has no food, move toward food
            else:
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)

    ##
    # getAttack
    # Not implemented
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  # don't care

    ##
    # registerWin
    # Not implemented
    ##
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass
