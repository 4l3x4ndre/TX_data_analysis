import os
import shutil

def main():
    import os


    sub_folder = 'Desert'
    model_folder = r'C:\Users\alexa\Documents\[UTC]\TX\total 15-11-2022\Corpus\Corpus\\' + sub_folder + '\\'
    trash = r'C:\Users\alexa\Documents\[UTC]\TX\total 15-11-2022\Corpus\doublon' + sub_folder + '\\'
    folder = r'C:\Users\alexa\Documents\[UTC]\TX\29-11-2022\moto_jpeg\\'
    valide_folder = r'C:\Users\alexa\Documents\[UTC]\TX\29-11-2022\Motos_png\\'

    # When a model folder is used
    """
    model_numbers = []
    for file_name in os.listdir(model_folder):
        model_numbers.append((file_name.split('-')[-1]).split(".png")[0])
        #print(model_numbers[-1])

    # numbers that has alreay been validate
    valide_numbers = []
    for file_name in os.listdir(valide_folder):
        valide_numbers.append((file_name.split('-')[-1]).split(".png")[0])

    """

    numbers = []
    count = 1
    # count increase by 1 in each iteration
    # iterate all files from a directory
    for file_name in os.listdir(folder):
        # Construct old file name
        source = folder + file_name

        # Adding the count to the new file name and extension
        number = (file_name.split('-')[-1]).split(".jpg")[0]
        numbers.append(number)
        destination = (file_name.split('-')[-1]).split(".jpg")[0] + '.png'

        shutil.copy(source, valide_folder + destination)
        pass

        # Renaming the file
        """
        # if it alreay exists : trash
        # else : rename it and keep it in the source folder
        if number in model_numbers:
            print("Already have a model : " + str(number))
            # os.rename(source, trash + destination)
        elif number in valide_numbers:
            print("Already have a valid : " + str(number))
        else:
            # os.rename(source, destination_folder+destination)
            shutil.copy(source, valide_folder + destination)
            continue
        """
        count += 1
    print('All Files Renamed')

    # verify the result
    print('New Names are')
    res = os.listdir(folder)
    print(res)


main()
