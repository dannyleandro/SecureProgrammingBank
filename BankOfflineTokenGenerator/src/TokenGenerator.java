import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Scanner;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class TokenGenerator {

	public static void main(String[] args) 
	{
		Scanner in = new Scanner(System.in);
		System.out.println("Ingrese su pin:");
		String pin = in.nextLine();
		System.out.println("Ingrese la cuenta de destino:");
		String dest = in.nextLine();
		System.out.println("Ingrese el monto:");
		String monto = in.nextLine();
		System.out.println("pin:" + pin + ",dest:" + dest + ",monto:" + monto);
		pin = hmacDigest(pin, "ZG6PLNRAKV6EMH5P2WVSG50B67IDR7UI", "HmacSHA256");
		in.close();
		while(true)
		{
			String tiempo = String.valueOf(System.currentTimeMillis()).substring(0, String.valueOf(System.currentTimeMillis()).length()-5);
			String message = pin + dest + monto + tiempo;
			try 
			{
				String digest = hmacDigest(message, "ZG6PLNRAKV6EMH5P2WVSG50B67IDR7UI", "HmacSHA1");
				digest = digest.replaceAll("[^0-9]", "");    
				System.out.println(digest.substring(0,8));
				Thread.sleep(100000);
			} 
			catch (InterruptedException e) 
			{
				e.printStackTrace();
			}
		}
	}	

	public static String hmacDigest(String msg, String keyString, String algo) {
		String digest = null;
		try {
			SecretKeySpec key = new SecretKeySpec((keyString).getBytes("UTF-8"), algo);
			Mac mac = Mac.getInstance(algo);
			mac.init(key);

			byte[] bytes = mac.doFinal(msg.getBytes("ASCII"));

			StringBuffer hash = new StringBuffer();
			for (int i = 0; i < bytes.length; i++) {
				String hex = Integer.toHexString(0xFF & bytes[i]);
				if (hex.length() == 1) {
					hash.append('0');
				}
				hash.append(hex);
			}
			digest = hash.toString();
		} catch (UnsupportedEncodingException e) {
		} catch (InvalidKeyException e) {
		} catch (NoSuchAlgorithmException e) {
		}
		return digest;
	}
}
