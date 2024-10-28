# ICEY_Agent
This is an AI agent for game ICEY
Built based on **ResNet** and **Reinforcement Learning**, create an AI agent for ICEY

# Code configure
- Most training configuration is in `train.py`
- `Agent.py` gets output actions from our mode
- `DQN.py` is the learning algorithm
- `Model.py` defines the model we use
- `ReplayMemory.py` defines the experience pool for learning
- `Actions.py` defines actions for ICEY and restart game script
- `GetHp.py` help us get our hp, boss hp, location (Using **Cheat Engine** to find your own process)
- `SendKey.py` is the API we use to send keyboard event to windows system.
- `GetScreen.py` is used to get screenshot of the game
- `Helper.py` defines multiple reward fucntions, and other functions we may use
