def batsmanBonusPoints(runs, out, balls, sRate):
    runsPoints = 0
    if runs >= 30 and runs < 50:
        runsPoints = 5
    elif runs >= 50 and runs < 100:
        runsPoints = 10
    elif runs >= 100:
        runsPoints = 20
    elif runs == 0 and out != 'not out':
        runsPoints = -10
    else:
        runsPoints = 0
    
    srPoints = 0
    if balls >= 10:
        if sRate > 170:
            srPoints = 15
        elif sRate >= 150.01 and sRate <= 170:
            srPoints = 10
        if sRate >= 130 and sRate <= 150:
            srPoints = 5
        elif sRate >= 60 and sRate <= 70:
            srPoints = -5
        elif sRate >= 50 and sRate <= 59.99:
            srPoints = -10
        elif sRate < 50:
            srPoints = -15
    
    return runsPoints + srPoints