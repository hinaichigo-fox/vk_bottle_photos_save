import asyncio
from vkbottle.bot import Bot, Message, BotLabeler
from vkbottle import API, Text, LoopWrapper
from vkbottle.http import SingleAiohttpClient
from vkbottle import PhotoMessageUploader
from aiohttp import TCPConnector
import aiohttp
import os
import urllib.request

labeler = BotLabeler()

#запуск бота 
async def main(loop_wrapper: LoopWrapper):
	global photo_uploader
	bot = Bot(api=API(token="Ваш токен", http_client=SingleAiohttpClient(connector=TCPConnector(verify_ssl=False))), loop_wrapper=loop_wrapper, labeler=labeler)
	photo_uploader = PhotoMessageUploader(bot.api)
	await bot.run_polling()

#функция сохранения картинок
async def download_photo(url: str, filename: str):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response: #конектимся с сайтом картинок
			if response.status == 200: #если ответ 200
				os.makedirs("photos", exist_ok=True) #делаем папку photos
				file_name = filename #берем имя файла
				urllib.request.urlretrieve(url, file_name) #сохраняем пикчу
				return f"Фото сохранено как photos/{filename}" #возвращаем то что пикча сохранена
			else:
				return "Ошибка при загрузке фото" #если ошибка и это возвращаем


@labeler.message()
async def handle_answer(message: Message):
	user_id = message.from_id #получаем юзер айди
	ms  = await message.get_full_message() #получаем полностью смс
	atts = ms.get_attachment_strings()[0] #получаем первый аттач
	if ms.attachments and ms.attachments[0].photo: #если аттач фото
		photo_sizes = ms.attachments[0].photo.sizes #получаем все размеры
		max_size = max(photo_sizes, key=lambda size: size.height if size.height else size.width) #получаем максимальный
		max_photo_url = max_size.url
		await message.answer(f"Ссылка на фото максимального размера: {max_photo_url}") #бот кидает ссылку на фото
		download_status = await download_photo(max_photo_url, f"photos/{user_id}.jpg") #скачиваем картинку
		await message.answer(download_status) #отправляем смс сохранилась ли картинка
		photo = await photo_uploader.upload(file_source=f"/disks/e/боты/goida_bot/photos/{user_id}.jpg") #теперь загружаем эту картинку
		await message.answer(attachment=photo) #отправялем ее как аттач




if __name__ == "__main__":
	loop_wrapper = LoopWrapper()
	loop_wrapper.on_startup.append(main(loop_wrapper))
	loop_wrapper.run()
