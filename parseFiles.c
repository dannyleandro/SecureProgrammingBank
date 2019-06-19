#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
	printf("Start C program\n");
	printf("main begins");
	FILE * fp;
    char * line = NULL;
    size_t len = 0;
    ssize_t read;

    fp = fopen("files/TransactionFile.txt", "r");
    if (fp == NULL)
	{
		printf("File not found");
        exit(EXIT_FAILURE);
	}
	printf("StartReadingfile");
	char str[255];
	while (getline(&line, &len, fp) != -1) 
	{
		strcat(str, line);
		strcat(str, ";");
    }
	printf(str);
    fclose(fp);
    if (line)
        free(line);
    exit(EXIT_SUCCESS);
	printf("Finish C program\n");
}
