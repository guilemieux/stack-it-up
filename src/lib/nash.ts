const teamA = [
    2000,
    1800,
    1600,
    1400,
    1200,
    1000,
]

const teamB = [
    2400,
    2000,
    1600,
    1200,
    800,
    400,
]

const N_STRATEGIES = 720  // 6!

// Map all the permutations on 6 elements to a number between 0 and 719
const ID_TO_STRATEGY = new Map<number[], number>()
for (const permutation of permutator([1, 2, 3, 4, 5, 6])) {
    
}



function permutator(inputArr: number[]): number[][] {
    let result: number[][] = []

    const permute = (arr: number[], m: number[] = []) => {
        if (arr.length === 0) {
            result.push(m)
        } else {
            for (let i = 0; i < arr.length; i++) {
                let curr = arr.slice()
                let next = curr.splice(i, 1)
                permute(curr.slice(), m.concat(next))
            }
        }
    }

    permute(inputArr)

    return result
}



export function winProbability(playerARating: number, playerBRating: number) {
    // Returns the probability of player A winning against player B
    const diff = playerARating - playerBRating
    const odds = Math.pow(10, diff / 400)
    return odds / (odds + 1)
}


