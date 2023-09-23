import { winProbability } from "@/lib/nash"

export default function Home() {
  const winProb = winProbability(1600, 1700)

  return (
    <h1>{winProb}</h1>
  )
}
