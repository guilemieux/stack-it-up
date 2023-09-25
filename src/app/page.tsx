import getPlayer from "@/lib/utrapi"

export default async function Home() {
  const player = await getPlayer("215710")

  return (
    <main>{player.firstName}</main>
  )
}
