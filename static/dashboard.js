import { getUserGuilds } from './user_guilds.js';

// Expose getUserGuilds globally for use anywhere
window.getUserGuilds = getUserGuilds;

// Redirect to /login if not logged in
(async function () {
    const data = await getUserGuilds();
    if (!data || !data.user) {
        window.location.href = '/login';
    }
})();

async function fetchGuilds() {
    console.log('fetchGuilds called');
    const data = await getUserGuilds();
    if (!data) {
        console.log('Failed to fetch user guilds');
        return;
    }
    console.log('Fetched guild data:', data);
    const guildList = document.getElementById('guildList');
    if (data.guilds && data.guilds.length > 0) {
        // Always show all servers the bot is in
        const botGuilds = data.guilds.filter(g => g.bot_in);
        // Add admin servers not already in botGuilds, up to 6 total
        const adminGuilds = data.guilds.filter(g => (g.permissions & 0x8) === 0x8 && !g.bot_in);
        const combined = botGuilds.concat(adminGuilds).slice(0, 6);
        guildList.innerHTML = combined.map(g => {
            let iconUrl = g.icon ? `https://cdn.discordapp.com/icons/${g.id}/${g.icon}.png` : 'https://cdn.discordapp.com/embed/avatars/0.png';
            let btn = g.bot_in
                ? `<button class=\"manage-btn\" onclick=\"window.location.href='/manage/${g.id}'\">Manage</button>`
                : `<a href=\"https://discord.com/oauth2/authorize?client_id=1404896235785293925&scope=bot+applications.commands&permissions=8&guild_id=${g.id}\" class=\"invite-btn\" target=\"_blank\">Invite</a>`;
            return `
                <div class=\"server-card\">
                    <img class=\"server-avatar\" src=\"${iconUrl}\" alt=\"Server Icon\">
                    <div class=\"server-name\">${g.name}</div>
                    ${btn}
                </div>
            `;
        }).join('');
    } else {
        guildList.innerHTML = '<p style=\"text-align:center;color:#b9bbbe;\">No servers found. Please login with Discord.</p>';
    }
}

window.fetchGuilds = fetchGuilds;
document.addEventListener('DOMContentLoaded', fetchGuilds);
console.log('dashboard.js loaded');
