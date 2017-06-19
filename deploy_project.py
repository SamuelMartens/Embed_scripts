import os
from os.path import isdir, join, isfile

def find_proj_file(current_dir_path):
    print "Looking for VS project file..."
    number_of_proj_files = 0
    path_to_proj_file = ""
    
    for root, dirs, files in os.walk(current_dir_path):
        for f in files:
            filename = os.path.join(root, f).strip()
            if filename.endswith("vcxproj"):
                print "Found VS project file " + filename
                number_of_proj_files += 1
                # We assume that there will only one project file, so no need to worries all
                # project files names. But anyway, lets check all proj files to give an appropriate error
                path_to_proj_file = filename

    if number_of_proj_files > 1:
        raise Exception("More that 1 project files")
    elif not number_of_proj_files:
        raise Exception("Project file not found")
    
    return path_to_proj_file

def get_additional_include_list(current_dir_path, proj_dir_name):
    print "Checking directories which will be additionaly included in project path..."
    # Ignore folders list
    dir_ignore_list = ["mbed", "BUILD"]
    dir_ignore_list.append(proj_dir_name)

    # Add to list top level directories
    dir_list = [join(current_dir_path, d) for d in os.listdir(current_dir_path) if isdir(join(current_dir_path, d)) and \
                not d.startswith(".") and d not in dir_ignore_list]

    # Mbed header file is not on the top level, so we need to add it in special way
    mbed_dir = [join(current_dir_path,"mbed", d) for d in os.listdir(join(current_dir_path, "mbed")) \
                if isdir(join(current_dir_path,"mbed", d)) and not d.startswith(".")]

    if not len(mbed_dir):
        raise Exception("No mbed library directory found")
    elif len(mbed_dir) > 1:
        raise Exception("Too many mbed library verisons in mbed dir")

    dir_list.append(mbed_dir[0])

    # This one is hardcoded so it possible to get erros. Usable only fot LPC1768
    dir_list.append(mbed_dir[0] + "\\TARGET_LPC1768\\TARGET_NXP\\TARGET_LPC176X\\TARGET_MBED_LPC1768")

    print "List of additionaly include directories:"
    for d in dir_list:
        print d
   
    return dir_list

def in_special_include_folder(folder, special_include_list):
    for index, include_folder in enumerate(special_include_list):
        if folder.find(include_folder) != -1:
            return index
    return -1

def Include_file(project_text, include_tag, include_index, include_item):
    project_text.insert(include_index, "<" + include_tag + " Include=\"" + join("..", include_item) + "\"/> \n")    

def include_folder_file(folder, file_text, include_index, extension, include_tag):
    # In each item represents first - special directory, second - name of files, that should be included only
    special_include_folders = [
        "mbed",
        "TARGET_MBED_LPC1768",
        "PinDetect", 
        ]

    special_include_files = [
            ["mbed.h"],
            ["PinNames.h"],
            ["PinDetect.h"]
        ]

    included_files = 0
    
    for item in os.listdir(folder):
        item = join(folder, item)
        if isfile(item) and item.endswith("." + extension):
            # Special folders is where we not include all headers
            special_index = in_special_include_folder(folder, special_include_folders)
            # Does it is special folder
            if special_index == -1 or (special_index != -1 and (item.split("\\")[-1] in special_include_files[special_index])):
                Include_file(file_text, include_tag, include_index, item)
                included_files += 1
    return included_files
            

def modify_proj_file(proj_file_path, include_dirs_list):
    print "Including additional directories in VS project file..."
    # List of preprocessor definitions that should be inserted in proj file
    preprocessor_definitions_list = ["DEVICE_CAN"]
    
    with open(proj_file_path, 'r+') as proj_file:
        file_text = proj_file.readlines()
        compile_section_entered = False
        content_modified = False
            
        for i,line in enumerate(file_text):
            line = line.strip()
            
            if line == "<ClCompile>" and not content_modified:
                compile_section_entered = True
            elif line == "</ClCompile>":
                compile_section_entered = False
            elif line.startswith("<SDLCheck>") and compile_section_entered and not content_modified:
                # Additionally include dirs
                if not file_text[i+1].strip().startswith("<AdditionalIncludeDirectories>"):
                    file_text.insert(i, "<AdditionalIncludeDirectories>" + ";".join(include_dirs_list) + \
                                    ";%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories> \n")
                else:
                    print "Project already contains some additionaly include directories, nothing added. \
                            Remove all additionally include dirs and run this script again" 
                # Preprocessor definitions
                if not file_text[i+1].strip().startswith("<PreprocessorDefinitions>"):
                    print "List of preprocessor definitions, that should be inserted:"
                    for definit in preprocessor_definitions_list:
                        print definit
                
                    file_text.insert(i - 1,"<PreprocessorDefinitions>" + ";".join(preprocessor_definitions_list) + \
                                 ";%(PreprocessorDefinitions)</PreprocessorDefinitions> \n")
                else:
                    print "Project already contains preprocessor definitions, nothing added. \
                            Remove all preprocessor definitions and run this script again"

                content_modified = True
            elif line == "<ItemGroup>" and len(file_text) >= i + 1 and file_text[i+1].strip() == "</ItemGroup>":
                included_files = 0
                
                print "Including *.cpp and *.h files in project"
                
                # Adding *.cpp files
                for include_dir in include_dirs_list:
                    included_files += include_folder_file(include_dir, file_text, i + 1, "cpp", "ClCompile")
                # Explicitly include main.cpp file
                Include_file(file_text, "ClCompile", i + 1, "..\\main.cpp")
                included_files += 1
                    
                # Adding *.h files
                file_text.insert(i + included_files + 2, "<ItemGroup> \n")
                file_text.insert(i + included_files + 3, "</ItemGroup> \n")
                for include_dir in include_dirs_list:
                    included_files += include_folder_file(include_dir, file_text, i + included_files + 3, "h", "ClInclude")
                
                print "Included " + str(included_files) + " in project."
                break

        # Rewrite file
        proj_file.seek(0)
        for line in file_text:
            proj_file.write(line)
        proj_file.truncate()
            

def main():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    proj_file_path = find_proj_file(current_dir_path)
    addition_inc = get_additional_include_list(join(current_dir_path, ".."), proj_file_path.split("\\")[-1].split(".")[0])
    modify_proj_file(proj_file_path, addition_inc)

if __name__ == "__main__":
    main()
