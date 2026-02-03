# Schelling's Model of Segregation
A toroidal-grid implementation of Thomas Schelling's famous model of segregation. This project simulates how even a generally tolerant society (tolerance of each individual is high) can lead to wide scale societal segregation

## Features
- **Toroidal Grid:** Uses a toroidal (wrap-around) board, simulating an infinite surface to remove any boundary bias.
- **Visual Mode:** Uses `pygame` to see how the board evolves over time, and `matplotlib` to graph time series data of 'unhappy agents' and 'measure of segregation'
- **Non-Visual Mode:** Optimised background processing that disables rendering to maximise speed.
- **Multiprocessing:** In non-visual mode, using `multiprocessing` utilises all CPU-cores to run multiple simulations in parallel.
- **Data Collection:** Automatically saves the data to a .csv for later graphing

## Installation
1. **Clone the repo:**
    ```bash
    git clone [https://github.com/arnavlul/schellings-segregation-model.git](https://github.com/arnavlul/schellings-segregation-model/)
    cd schellings-segregation-model
    ```

2. **Install the required dependencies:**
    ```bash
    pip install numpy matplotlib pygame
    ```

## Usage
There are 2 ways to run the simulation:

1. Single simulation:
```bash
python mode.py
```
