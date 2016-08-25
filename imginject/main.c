// imginject
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "filewrite.h"

#define handle_error(msg) \
do { perror(msg); exit(EXIT_FAILURE); } while (0)
	

int main( int argc, char** argv)
{
	
	if ( argc == 1 )
	{
	puts("Usage: ./main image ");
	}  
	if ( argc == 2 )
	{
		uint8_t *memblock;
		
		char parbuffer[6][512];
		
		int fd;
		struct stat sb;
		
		FILE * fp;
		char * line = NULL;
		size_t len = 0;
		ssize_t read;
			
		fp = fopen("offsets.txt", "r");
		if (fp == NULL)
			exit(EXIT_FAILURE);
		
		fd = open(argv[1], O_RDONLY);
		
		fstat(fd, &sb);

		printf("Size: %lu\n", (uint64_t)sb.st_size);
	  
		memblock = mmap(NULL, sb.st_size, PROT_WRITE, MAP_PRIVATE, fd, 0);
		if (memblock == MAP_FAILED) handle_error("mmap");

		while ((read = getline(&line, &len, fp)) != -1) {
			uint32_t off, ct, w, h;
			char * token = strtok(line, ":");
			if(line[0] != '#')
			{
				int j = 0;
				while(token != NULL)
				{
					strcpy(parbuffer[j], token);
					token = strtok(NULL, ":");
					j++;
				}
				sscanf(parbuffer[1], "%x",  &off);
				sscanf(parbuffer[2], "%d", &w);
				sscanf(parbuffer[3], "%d", &h);
				sscanf(parbuffer[4], "%d", &ct);
				printf("dumping element %s, size %d*%d, %d frames \n", parbuffer[0], w, h, ct);
				dump_element(parbuffer[0], memblock, off, ct, w, h);
			}
		}
		
		//dump_element("bootanim", memblock, 0xd292c, 7, 128, 64 );
	  
		munmap(memblock, sb.st_size);
		close(fd);
		
		fclose(fp);
		if (line)
			free(line);
		exit(EXIT_SUCCESS);
		
		return 0;
	}
  return 0;
}

