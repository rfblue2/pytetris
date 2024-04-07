# PyTetris

Tetris clone in python.

This project is managed by Pipenv.  In general do development work while shelled
into pipenv:
```
pipenv shell
```
Leave the shell by typing
```
exit
```

Common commands outside the shell
```
pipenv install <package>
pipenv run python main.py
```

### TODO List:
- Top Out conditions (game over)
- Hold
- Next Queue
- Ghost Piece
- CCW Rotation
- Pause (requires a way to pause existing timers)
- Extended Lockdown
- Back-to-Back, hard/soft drop scoring
- T-spins