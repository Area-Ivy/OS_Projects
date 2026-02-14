import {Page, Memory, MemoryState} from './classes.js'

const TOTAL_INSTRUCTIONS = 320
const MEMORY_SIZE = 4
const PAGES_COUNT = 32

function generateInstructionSequence() {
    const executionOrder = []
    let count = 0
    
    while (count < TOTAL_INSTRUCTIONS) {
        const m = Math.floor(Math.random() * TOTAL_INSTRUCTIONS)
        executionOrder.push(m)
        count++
        
        if (m + 1 < TOTAL_INSTRUCTIONS && count < TOTAL_INSTRUCTIONS) {
            executionOrder.push(m + 1)
            count++
        }
        
        if (m > 0 && count < TOTAL_INSTRUCTIONS) {
            const m1 = Math.floor(Math.random() * m)
            executionOrder.push(m1)
            count++
            
            if (m1 + 1 < m && count < TOTAL_INSTRUCTIONS) {
                executionOrder.push(m1 + 1)
                count++
            }
        }
        
        if (m + 2 < TOTAL_INSTRUCTIONS && count < TOTAL_INSTRUCTIONS) {
            const m2 = m + 2 + Math.floor(Math.random() * (TOTAL_INSTRUCTIONS - 2 - m))
            executionOrder.push(m2)
            count++
            
            if (m2 + 1 < TOTAL_INSTRUCTIONS && count < TOTAL_INSTRUCTIONS) {
                executionOrder.push(m2 + 1)
                count++
            }
        }
    }
    if (executionOrder.length > TOTAL_INSTRUCTIONS) {
        executionOrder.pop()
    }
    
    return executionOrder
}

function initializeSimulation(algorithm) {
    return {
        log: new MemoryState(),
        pages: Array.from({length: PAGES_COUNT}, (_, i) => new Page(i)),
        memory: new Memory(MEMORY_SIZE, algorithm),
        instructions: generateInstructionSequence(),
        pageFaults: 0,
        count: 0
    }
}

function calculatePageFaultRate(pageFaults) {
    return pageFaults / TOTAL_INSTRUCTIONS
}

export function fifoSimulation() {
    const sim = initializeSimulation('FIFO')
    let index = 0
    
    for (const instruction of sim.instructions) {
        sim.count++
        const pageId = Math.floor(instruction / 10)
        
        if (!sim.memory.hasInstruction(instruction)) {
            const removedPage = sim.memory.pages.length >= sim.memory.size ? 
                sim.memory.pages[index].id : null
                
            sim.memory.pages[index] = sim.pages[pageId]
            sim.memory.lastUsedTime[index] = sim.count
            sim.pageFaults++
            
            sim.log.addLog(sim.count, instruction, sim.memory, true, index, removedPage)
            
            index = (index + 1) % MEMORY_SIZE
        } else {
            sim.log.addLog(sim.count, instruction, sim.memory, false, null, null)
        }
    }
    
    return {
        pageFaults: sim.pageFaults, 
        pageFaultRate: calculatePageFaultRate(sim.pageFaults), 
        logs: sim.log.logs
    }
}

export function lruSimulation() {
    const sim = initializeSimulation('LRU')
    
    for (const instruction of sim.instructions) {
        sim.count++
        const pageId = Math.floor(instruction / 10)
        
        if (!sim.memory.hasInstruction(instruction, sim.count)) {
            let index = sim.memory.pages.findIndex(page => page === undefined)
            
            if (index === -1) {
                index = sim.memory.lastUsedTime.indexOf(Math.min(...sim.memory.lastUsedTime))
            }
            
            const removedPage = sim.memory.pages[index] ? sim.memory.pages[index].id : null
            
            sim.memory.pages[index] = sim.pages[pageId]
            sim.memory.lastUsedTime[index] = sim.count
            sim.pageFaults++
            
            sim.log.addLog(sim.count, instruction, sim.memory, true, index, removedPage)
        } else {
            sim.log.addLog(sim.count, instruction, sim.memory, false, null, null)
        }
    }
    
    return {
        pageFaults: sim.pageFaults, 
        pageFaultRate: calculatePageFaultRate(sim.pageFaults), 
        logs: sim.log.logs
    }
} 