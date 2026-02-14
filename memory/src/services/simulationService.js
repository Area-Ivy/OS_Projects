import { fifoSimulation, lruSimulation } from '../utils.js'

export function runSimulation(simulationFunction) {
  const startTime = performance.now()
  const result = simulationFunction()
  const endTime = performance.now()
  
  return {
    ...result,
    executionTime: Number((endTime - startTime).toFixed(2))
  }
}

export function getSimulationName(simulationFunction) {
  return simulationFunction === fifoSimulation ? 'FIFO' : 'LRU'
}

export const simulationAlgorithms = {
  fifo: fifoSimulation,
  lru: lruSimulation
} 