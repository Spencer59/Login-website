// user_guilds.js
// Provides a function to fetch user guilds and return the data (Promise)

export async function getUserGuilds() {
    try {
        const res = await fetch('/user_guilds');
        if (!res.ok) return null;
        const data = await res.json();
        return data;
    } catch (e) {
        return null;
    }
}
