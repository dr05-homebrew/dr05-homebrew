CFLAGS += -std=gnu99 -Wall

imginject: filewrite.o main.o
	$(CC) -o $@ $+

main.o: filewrite.h
