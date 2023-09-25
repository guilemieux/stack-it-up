export default async function getPlayer(playerId: string) {
    const response = await fetch(
        `https://api.universaltennis.com/v1/player/${playerId}/profile`,
        {
            headers: {
                cookie: `jwt=${process.env.UTR_JWT};`
            }
        }
    )
    return await response.json()
}