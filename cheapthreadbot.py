import discord
import json
from os import getenv
from datetime import datetime as dt

from infrastructure.apiclient import apiClient

# オブジェクトを取得
discordClient = discord.Client()

# 文字列を空白区切りでリスト化
def split_command(content):
    args = content.replace("　", " ").split(" ")
    while "" in args:
        args.remove("")
    return args


def check_validation(params, errors):
    return errors


async def show_list_information(ctx, params: dict):
    r = apiClient.fetch_lists(params)
    info_str = " "
    for key in params:
        info_str += f"{key}: {params[key]},"
    if r.status_code == 200:
        data = json.loads(r.text)
        embed = discord.Embed(title=f"検索結果", description=info_str[:-1], color=0x00FF00)
        for lst in data:
            embed.add_field(
                name=f"{lst['id']}: {lst['title']}",
                value=f"連: {'○' if lst['ready_to_turn_default_gacha'] else '☓'}, 円: {'○' if lst['ready_to_turn_price_gacha'] else '☓'}, kcal: {'○' if lst['ready_to_turn_calorie_gacha'] else '☓'}",
                inline=False,
            )
    else:
        embed = discord.Embed(
            title="ERROR", description="Something is wrong", color=0xFF0000
        )
    await ctx.channel.send(embed=embed)


async def show_gacha_information(ctx, params: dict, list_id, kind):
    r = apiClient.fetch_gachas(params, list_id, kind)
    info_str = " "
    for key in params:
        info_str += f"{key}: {params[key]},"
    if r.status_code == 200:
        data = json.loads(r.text)
        embed = discord.Embed(title=f"検索結果", description=info_str[:-1], color=0x00FF00)
        if kind == "default":
            for element in data:
                embed.add_field(
                    name=f"{element['name']}",
                    value=f"{'￥'+str(element['price']) if element['price'] else ''}　{str(element['calorie']) + 'kcal' if element['calorie'] else ''}",
                    inline=False,
                )
        else:
            embed.title = (
                "検索結果 計"
                + ("￥" if kind == "price" else "")
                + str(data[0])
                + ("kcal" if kind == "calorie" else "")
            )
            for element in data[1]:
                embed.add_field(
                    name=f"{element['name']}",
                    value=f"{'￥'+str(element['price']) if element['price'] else ''}　{str(element['calorie']) + 'kcal' if element['calorie'] else ''}",
                    inline=False,
                )
    else:
        embed = discord.Embed(title="ERROR", description=r.text, color=0xFF0000)
    await ctx.channel.send(embed=embed)


async def show(ctx, args):
    params = {}
    errors = []
    if len(args) < 2:
        errors.append({"name": "引数エラー", "value": "引数が少なすぎます"})
    elif len(args) == 3:
        params["q"] = args[2]
    elif len(args) > 3:
        errors.append({"name": "引数エラー", "value": "引数が多すぎます"})
    errors = check_validation(params, errors)
    if errors:
        embed = discord.Embed(title="hoge", description="fuga", color=0xFF0000)
        embed.title = "ERROR"
        embed.description = "Something is wrong"
        embed.color = 0xFF0000
        for err in errors:
            embed.add_field(name=err["name"], value=err["value"], inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await show_list_information(ctx, params)


async def gacha(ctx, args):
    permit_options = {
        "-d": "default",
        "-p": "price",
        "-c": "calorie",
        "--default": "default",
        "--price": "price",
        "--calorie": "calorie",
    }
    errors = []
    kind = "default"
    elements = []
    params = []
    if len(args) < 4:
        errors.append({"name": "引数エラー", "value": "引数が少なすぎます"})
    elif len(args) > 5:
        errors.append({"name": "引数エラー", "value": "引数が多すぎます"})
    for arg in args[2:]:
        if arg in permit_options:
            kind = permit_options[arg]
        else:
            elements.append(arg)
    if len(elements) != 2:
        errors.append({"name": "引数エラー", "value": "引数が不正です"})
    elif kind == "default":
        params = {"num": elements[1]}
    elif kind == "price":
        params = {"price": elements[1]}
    elif kind == "calorie":
        params = {"calorie": elements[1]}
    errors = check_validation(params, errors)
    if errors:
        embed = discord.Embed(title="hoge", description="fuga", color=0xFF0000)
        embed.title = "ERROR"
        embed.description = "Something is wrong"
        embed.color = 0xFF0000
        for err in errors:
            embed.add_field(name=err["name"], value=err["value"], inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await show_gacha_information(ctx, params, elements[0], kind)


# コマンド処理
async def exec_command(ctx, args):
    if args[1] == "list":
        await show(ctx, args)
    elif args[1] == "gacha":
        await gacha(ctx, args)


@discordClient.event
async def on_ready():
    # サーバー起動時に実行
    print("サーバーを起動します。")


@discordClient.event
async def on_message(ctx):
    # Botのメッセージは除外
    if ctx.author.bot:
        return
    # 文字列を空白区切りでリスト化
    args = split_command(ctx.content)
    # /wsmであれば実行
    if args[0] == "/cs":
        await exec_command(ctx, args)


# 実行
def main():
    discordClient.run(getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    main()
