import os

from parameters import graphs_pdf_directory_path, graphs_png_directory_path, jsons_directory_path


def delete_files_in_directory(directory, containing=None):
    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            print(f"The directory '{directory}' does not exist.")
            return

        # Get list of all files in the directory
        files = os.listdir(directory)

        # Iterate over each file and delete it
        for file_name in files:
            if containing and any(c not in file_name for c in containing):
                continue
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        print("All files in the directory have been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    containing = None
    # containing = ["1D", "seqcc"]

    delete_files_in_directory(graphs_pdf_directory_path, containing)
    delete_files_in_directory(graphs_png_directory_path, containing)
    delete_files_in_directory(jsons_directory_path, containing)
