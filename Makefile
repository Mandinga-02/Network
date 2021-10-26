CC = uvicorn
# Automatically reload after commiting change to code.
Flag = --reload

run:
	${CC} main:app ${Flag}