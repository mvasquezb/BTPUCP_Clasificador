/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package comparararchivos;
import java.io.File; 
import java.io.FileInputStream; 
import java.io.FileNotFoundException; 
import java.io.FileOutputStream; 
import java.io.FileWriter;
import java.io.IOException; 
import java.io.PrintWriter;
import java.sql.Date; 
import java.util.HashMap; 
import java.util.Iterator; 
import java.util.Map; 
import java.util.Set; 

import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.xssf.usermodel.XSSFSheet;
/**
 *
 * @author jose.gil
 */
public class CompararArchivos {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
        File excel1=null;
        FileInputStream fl1=null;
        XSSFWorkbook book1=null;
        
        File excel2=null;
        FileInputStream fl2=null;
        XSSFWorkbook book2=null;
        
        
        
        try{
            excel1 = new File("D:\\Users\\jose.gil\\Documents\\Anotaciones\\ProfesorB.xlsx");
            excel2 = new File("D:\\Users\\jose.gil\\Documents\\Anotaciones\\ProfesorD.xlsx");
            
            PrintWriter file=new PrintWriter("diferencias.txt","UTF-8");
            
            fl1=new FileInputStream(excel1);
            fl2=new FileInputStream(excel2);
            
            book1 = new XSSFWorkbook(fl1);
            book2 = new XSSFWorkbook(fl2);
            
            
            XSSFSheet sheet_A = book1.getSheetAt(0);
            XSSFSheet sheet_B = book2.getSheetAt(0);
            
            Iterator<Row> itrA = sheet_A.iterator();
            Iterator<Row> itrB = sheet_B.iterator();
            
            int totalDiferencias=0;
            int numFila=2;
            while(itrA.hasNext() && itrB.hasNext()){
                Row rowA = itrA.next();
                Row rowB = itrB.next();
                if(rowA.getRowNum()==0) continue;
                
                Iterator<Cell> cellitA=rowA.cellIterator();
                Iterator<Cell> cellitB=rowB.cellIterator();
                
                Cell celA = cellitA.next();
                Cell celB = cellitB.next();
                
                //Se esta en las celdas del numero de Aviso
                celA=cellitA.next();
                celB=cellitB.next();
                
                int numAvisoA=(int)celA.getNumericCellValue();
                int numAvisoB=(int)celB.getNumericCellValue();
                               
                
                if(numAvisoA!=numAvisoB){
                    System.out.println("Numero de Aviso: "+numAvisoA);
                    continue;
                }
                
                //Se esta en las celdas de la categoria
                celA=cellitA.next();
                celB=cellitB.next();
                
                String textA=celA.getStringCellValue();
                //System.out.println("Categoria A: "+textA);
                String textB=celB.getStringCellValue();
                //System.out.println("Categoria B: "+textB);
                
                if(!textA.equals(textB)){
                    System.out.println("Fila: "+numFila+" Numero de Aviso: "+numAvisoA+" Texto B: "+textA+" - Texto D: "+textB);
                    file.println("Fila: "+numFila+" Numero de Aviso: "+numAvisoA+" Texto B: "+textA+" - Texto D: "+textB);
                    totalDiferencias++;
                }
                
                numFila++;
            }
            
            System.out.println("\nTotal diferencias: "+totalDiferencias);
            file.println("\nTotal diferencias: "+totalDiferencias);
            
            file.close();
            
            
        }
        catch (FileNotFoundException fe) {
            fe.printStackTrace(); 
        } catch (IOException ie) {
            ie.printStackTrace(); }
        
    }
    
}
