export class Page {
    constructor(id) {
        this.id = id
        this.instructions = Array.from({length: 10}, (_, i) => id * 10 + i)
    }
}

export class Memory {
    constructor(size, method) {
        this.size = size
        this.method = method
        this.pages = []
        this.lastUsedTime = Array(4).fill(0)
    }

    hasInstruction(instruction, time = 0) {
        const pageIndex = this.pages.findIndex(page => 
            page && page.instructions.includes(instruction)
        )
        
        if (pageIndex !== -1) {
            if (this.method === 'LRU') {
                this.lastUsedTime[pageIndex] = time
            }
            return true
        }
        return false
    }
}

export class MemoryState {
    constructor() {
        this.logs = []
    }

    addLog(id, instructionId, memory, isPageFault, insertedBlock, removedPage) {
        const logEntry = {
            id,
            instructionId,
            pages: memory.pages.map(page => page ? page.id : '-'),
            isPageFault,
            insertedBlock: insertedBlock !== null ? insertedBlock + 1 : '-',
            removedPage: removedPage !== null ? removedPage : '-'
        }
        this.logs.push(logEntry)
    }
} 