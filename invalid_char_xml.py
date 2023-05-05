import re

# specify the path to your input file
input_file = "./file.xml"

# specify the path to the output file
output_file = "./file.xml"

# specify the encoding of your input and output files
input_encoding = "utf-8"
output_encoding = "utf-8"

# specify the regular expression pattern to match invalid characters
invalid_char_pattern = re.compile("[\x00-\x08\x0B\&#x1E\x0E-\x1F]")

# open the input file for reading and the output file for writing
with open(input_file, "r", encoding=input_encoding) as in_file, \
     open(output_file, "w", encoding=output_encoding) as out_file:
     
    # read in the input file
    data = in_file.read()
    
    # remove any invalid characters from the data
    cleaned_data = invalid_char_pattern.sub("", data)
    
    # write the cleaned data to the output file
    out_file.write(cleaned_data)