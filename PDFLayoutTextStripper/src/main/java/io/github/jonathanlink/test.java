package io.github.jonathanlink;

import java.awt.geom.Rectangle2D;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.Writer;
import java.util.*;
import org.apache.pdfbox.io.RandomAccessFile;
import org.apache.pdfbox.pdfparser.PDFParser;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

class GetWordLocationAndSize extends PDFTextStripper {

    public GetWordLocationAndSize() throws IOException {
        super();
    }

    @Override
    protected void writeString(String string, List<TextPosition> textPositions) throws IOException {
        String wordSeparator = getWordSeparator();
        List<TextPosition> word = new ArrayList<>();
        for (TextPosition text : textPositions) {
            String thisChar = text.getUnicode();
            if (thisChar != null) {
                if (thisChar.length() >= 1) {
                    if (!thisChar.equals(wordSeparator)) {
                        word.add(text);
                    } else if (!word.isEmpty()) {
                        printWord(word);
                        word.clear();
                    }
                }
            }
        }
        if (!word.isEmpty()) {
            printWord(word);
            word.clear();
        }
    }

    void printWord(List<TextPosition> word) {
        Rectangle2D boundingBox = null;
        StringBuilder builder = new StringBuilder();
        for (TextPosition text : word) {
            Rectangle2D box = new Rectangle2D.Float(text.getXDirAdj(), text.getYDirAdj(),
                    text.getWidthDirAdj(), text.getHeightDir());
            if (boundingBox == null)
                boundingBox = box;
            else
                boundingBox.add(box);
            builder.append(text.getUnicode());
        }
        double xCoordinate = boundingBox.getX();
        double yCoordinate = boundingBox.getY();
        double heightOfbbox = boundingBox.getHeight();
        double widthOfbbox = boundingBox.getWidth();

        int xIntegerValue = (int) xCoordinate;
        int yIntegerValue = (int) yCoordinate;
        int IntegerHeight = (int) heightOfbbox;
        int IntegerWidth = (int) widthOfbbox;

        System.out.println(builder.toString() + " [(X=" + xIntegerValue + ",Y=" + yIntegerValue
                + ") height=" + IntegerHeight + " width=" + IntegerWidth + "]");
    }
}

public class test {

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("Error: Insufficient arguments provided.");
            System.err.println("Usage: java Test <pdfFilePath> <page_number> <output_text_file>");
            return;
        }


        String pdfFilePath = args[0];
        // String page_number = args[1];
        // String outputTextFile = args[2];

        // // Print received arguments for debugging
        // System.out.println("PDF Path: " + pdfFilePath);
        // System.out.println("Page Number: " + page_number);
        // System.out.println("Output Text File: " + outputTextFile);
        String outputDir = "output";

        ensureDirectoryExists(outputDir);

        try {
            PDFParser pdfParser = new PDFParser(new RandomAccessFile(new File(pdfFilePath), "r"));
            pdfParser.parse();
            PDDocument pdDocument = new PDDocument(pdfParser.getDocument());
            PDFTextStripper pdfTextStripper = new PDFLayoutTextStripper();
            String extractedText = pdfTextStripper.getText(pdDocument);
            writeTextToFile(extractedText, outputDir + "/output.txt");
            System.out.println("Text extraction completed.");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            PDDocument document = PDDocument.load(new File(pdfFilePath));
            PDFTextStripper stripper = new GetWordLocationAndSize();
            stripper.setSortByPosition(true);
            stripper.setStartPage(0);
            stripper.setEndPage(document.getNumberOfPages());

            Writer dummy = new OutputStreamWriter(new ByteArrayOutputStream());
            try (FileWriter csvWriter = new FileWriter(outputDir + "/output.csv")) {
                System.setOut(new PrintStream(new OutputStream() {
                    @Override
                    public void write(int b) throws IOException {
                        csvWriter.write(b);
                    }
                }));

                stripper.writeText(document, dummy);
                System.out.println("Bounding box extraction completed.");
            } catch (IOException e) {
                e.printStackTrace();
            }

            document.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void ensureDirectoryExists(String dirPath) {
        File dir = new File(dirPath);
        if (!dir.exists()) {
            if (dir.mkdirs()) {
                System.out.println("Directory created: " + dirPath);
            } else {
                System.err.println("Failed to create directory: " + dirPath);
            }
        }
    }

    private static void writeTextToFile(String text, String filePath) {
        try (FileWriter fileWriter = new FileWriter(filePath)) {
            fileWriter.write(text);
            
        } catch (IOException e) {
            System.err.println("Error writing text to file: " + e.getMessage());
        }
    }
}