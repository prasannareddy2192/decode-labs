public class sample_code {

    private int[] stock;

    public sample_code(int size) {
        stock = new int[size];
    }

    public void addStock(int index, int amount) {
        stock[index] += amount;
    }

    public int getStock(int index) {
        return stock[index];
    }

    public static void main(String[] args) {
        sample_code manager = new sample_code(5);
        manager.addStock(5, 10);
        System.out.println(manager.getStock(5));
    }
}